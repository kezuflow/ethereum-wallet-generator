import random
import asyncio
import threading
import signal
import sys
from web3 import AsyncWeb3
from web3.providers.async_rpc import AsyncHTTPProvider
from eth_account import Account
from mnemonic import Mnemonic
from hashlib import pbkdf2_hmac
from playsound import playsound
import os

# Helios RPC endpoint
HELIOS_URL = "http://127.0.0.1:8545"

# Initialize AsyncWeb3
w3 = AsyncWeb3(AsyncHTTPProvider(HELIOS_URL))

# Enable HD Wallet Features
Account.enable_unaudited_hdwallet_features()

stop_event = threading.Event()


def signal_handler(sig, frame):
    print("\nGracefully stopping... Please wait...")
    stop_event.set()

signal.signal(signal.SIGINT, signal_handler)


def generate_mnemonic():
    """Generates a 12-word mnemonic phrase using BIP-39."""
    mnemo = Mnemonic("english")
    return mnemo.generate(strength=128)


def mnemonic_to_seed(mnemonic, passphrase=""):
    """
    Converts a mnemonic phrase to a seed using PBKDF2 with HMAC-SHA512.
    This matches MetaMask's seed generation process.
    """
    # BIP-39 specifies "mnemonic" + passphrase as the salt
    salt = "mnemonic" + passphrase
    # PBKDF2 with HMAC-SHA512, 2048 iterations, 64-byte seed
    seed = pbkdf2_hmac("sha512", mnemonic.encode("utf-8"), salt.encode("utf-8"), 2048, 64)
    return seed.hex()


def derive_private_key_and_address(seed):
    """
    Derives the private key and address from the seed using BIP-44.
    This matches MetaMask's derivation process.
    """
    # Derive the master key using BIP-32
    from bip_utils import Bip32Slip10Ed25519, Bip44, Bip44Coins, Bip44Changes

    # Convert the seed from hex to bytes
    seed_bytes = bytes.fromhex(seed)

    # Derive the BIP-44 wallet for Ethereum
    bip44_mst_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.ETHEREUM)
    bip44_acc_ctx = bip44_mst_ctx.Purpose().Coin().Account(0)
    bip44_chg_ctx = bip44_acc_ctx.Change(Bip44Changes.CHAIN_EXT)
    bip44_addr_ctx = bip44_chg_ctx.AddressIndex(0)

    # Get the private key and address
    private_key = bip44_addr_ctx.PrivateKey().Raw().ToHex()
    address = bip44_addr_ctx.PublicKey().ToAddress()

    return private_key, address


async def check_balance(address):
    """Fetches the balance of a given Ethereum address."""
    try:
        balance = await w3.eth.get_balance(address)
        return w3.from_wei(balance, 'ether')
    except Exception as e:
        return 0


async def check_transaction_count(address):
    """Fetches the transaction count of a given Ethereum address."""
    try:
        return await w3.eth.get_transaction_count(address)
    except Exception as e:
        return 0


def play_alert_sound():
    """Plays the alert sound."""
    sound_path = os.path.join("sound", "alert.wav")
    if os.path.exists(sound_path):
        playsound(sound_path)


async def save_to_file(wallet_info):
    """Saves wallet information to a file."""
    with open("wallets.txt", "a", encoding="utf-8") as file:
        file.write(wallet_info + "\n\n")


async def generate_wallet():
    """Generates a new wallet and checks its balance and transaction count."""
    mnemonic = generate_mnemonic()
    seed = mnemonic_to_seed(mnemonic)  # Generate seed using PBKDF2 with HMAC-SHA512
    private_key, address = derive_private_key_and_address(seed)  # Derive private key and address

    balance = await check_balance(address)
    transaction_count = await check_transaction_count(address)

    # Displaying all wallets in the terminal
    print(f"🟢 Checking Wallet: {address} 💰 Balance: {balance} ETH 🔴 Transactions: {transaction_count}")

    if balance > 0 or transaction_count > 0:  # Save only if balance or transactions are present
        wallet_info = (
            f"🟢 Wallet: {address}\n"
            f"🔑 Private Key: {private_key}\n"
            f"📝 Mnemonic: {mnemonic}\n"
            f"💰 Balance: {balance} ETH\n"
            f"🔴 Transactions: {transaction_count}"
        )
        await save_to_file(wallet_info)
        play_alert_sound()  # Play alert sound if condition is met


async def main(batch_size=5):
    tasks = [generate_wallet() for _ in range(batch_size)]
    await asyncio.gather(*tasks)


def start_thread(batch_size, delay):
    try:
        while not stop_event.is_set():
            asyncio.run(main(batch_size))
            asyncio.run(asyncio.sleep(delay))
    except KeyboardInterrupt:
        print("\nStopping gracefully... Please wait...")
        stop_event.set()


if __name__ == "__main__":
    batch_size = 10
    delay = 1

    thread = threading.Thread(target=start_thread, args=(batch_size, delay), daemon=True)
    thread.start()

    try:
        while thread.is_alive():
            thread.join(0.1)
    except KeyboardInterrupt:
        print("\nMain process interrupted. Stopping...")
        stop_event.set()
        thread.join()
