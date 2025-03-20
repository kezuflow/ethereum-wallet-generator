# Wallet Generator

This project generates Ethereum wallets, checks their balances and transaction counts, and saves the wallet information if certain conditions are met. It also plays an alert sound when a wallet with a balance or transactions is found.

## Features

- Generates Ethereum wallets using a 12-word mnemonic phrase.
- Checks the balance and transaction count of each generated wallet.
- Saves wallet information to a file if the wallet has a balance or transactions.
- Plays an alert sound when a wallet with a balance or transactions is found.
- Continuously generates wallets in batches with a specified delay between batches.

## Requirements

- Python 3.7+
- `web3` library
- `eth_account` library
- `mnemonic` library
- `playsound` library
- An Ethereum node (e.g., Helios RPC endpoint)

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/your-username/wallet-generator.git
    cd wallet-generator
    ```

2. Install the required libraries:

    ```sh
    pip install web3 eth_account mnemonic playsound
    ```

3. Ensure you have an Ethereum node running and update the `HELIOS_URL` variable in `main.py` with your node's URL.

## Usage

1. Run the script:

    ```sh
    python main.py
    ```

2. The script will:
    - Generate wallets in batches.
    - Check the balance and transaction count of each generated wallet.
    - Display wallet information in the terminal.
    - Save wallet information to `wallets.txt` if the wallet has a balance or transactions.
    - Play an alert sound when a wallet with a balance or transactions is found.

3. To stop the script gracefully, press `Ctrl+C`.

## Configuration

- `batch_size`: Number of wallets to generate in each batch. Default is 4.
- `delay`: Delay in seconds between each batch. Default is 0.2 seconds.

You can modify these values in the `main.py` file:

```python
if __name__ == "__main__":
    batch_size = 4
    delay = 0.2
