import random
import asyncio
import threading
import signal
import sys
from web3 import AsyncWeb3
from web3.providers.async_rpc import AsyncHTTPProvider
from eth_account import Account
from mnemonic import Mnemonic
from playsound import playsound  # Import playsound for playing sound
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
    """Generates a 12-word mnemonic phrase."""
    mnemo = Mnemonic("english")
    return mnemo.generate(strength=128)


def mnemonic_to_private_key(mnemonic):
    """Generates a private key from a mnemonic phrase."""
    seed = Mnemonic.to_seed(mnemonic)
    account = Account.from_mnemonic(mnemonic)
    return account._private_key.hex(), account.address  # Changed privateKey to _private_key


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
    private_key, address = mnemonic_to_private_key(mnemonic)

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
