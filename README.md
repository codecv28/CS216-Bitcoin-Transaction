# CS216 - Bitcoin Transaction Validation: Legacy vs. SegWit

This repository contains the code and analysis for generating, broadcasting, and validating Bitcoin Legacy (P2PKH) and SegWit (P2SH-P2WPKH) transactions. All transactions were executed on a local `regtest` Bitcoin network. 

The primary objective of this project is to analyze the structural differences between Legacy and SegWit transactions, specifically demonstrating the "Witness Discount" by comparing transaction sizes and virtual sizes (`vSize`), and to validate the underlying cryptographic scripts using the Bitcoin Debugger (`btcdeb`).

## Byzantine - Team Members
* Mane Abhishek Ganesh - 240001043
* Dhoke Vinod Eknath - 240001025
* Chetan Verma - 240001022
* Sahil Hedaoo - 240041032

## Project Structure
* `part1.py`: Python script that creates a fresh wallet, funds a Legacy address, generates a P2PKH transaction (A -> B), spends it (B -> C), and extracts the locking/unlocking scripts.
* `part2.py`: Python script that replicates the workflow using P2SH-P2WPKH (SegWit) addresses, extracting the segregated witness data and demonstrating the reduction in virtual size.
* `bitcoin.conf`: Configuration file used to instantiate the local Bitcoin Core `regtest` node with the required RPC settings.
* `Report.pdf`: The comprehensive final report containing transaction IDs, script analysis, `btcdeb` stack execution screenshots, and a detailed explanation of the SegWit Witness Discount.

## Prerequisites
To run this project locally, you need the following installed:
* **Bitcoin Core** (`bitcoind` and `bitcoin-cli`)
* **Python 3.x**
* **python-bitcoinrpc** (Install via: `pip install python-bitcoinrpc`)
* **btcdeb** (Bitcoin Debugger for script validation)

## Setup & Execution Instructions

### Set Up the Python Virtual Environment
It is highly recommended to run this project inside a virtual environment to manage dependencies cleanly.

```bash
# Create the virtual environment
python3 -m venv venv

# Activate the virtual environment (macOS/Linux)
source venv/bin/activate

# Activate the virtual environment (Windows)
venv\Scripts\activate

# Install the required dependencies
pip install -r requirements.txt
```

### 1. Start the Local Bitcoin Node
Launch the Bitcoin Core daemon in `regtest` mode using the provided configuration file:
```bash
bitcoind -regtest -daemon -conf=$(pwd)/bitcoin.conf
```

### 2. Execute Part 1 (Legacy P2PKH)
Run the first script to generate the legacy transactions:

```bash
python part1.py
```
Output: This will print the TXIDs, the decoded scriptPubKey (locking script), the scriptSig (unlocking script), and the physical/virtual size metrics for the Legacy transactions.

### 3. Execute Part 2 (SegWit P2SH-P2WPKH)
Run the second script to generate the SegWit transactions:
```bash 
python part2.py
```
Output: This will print the TXIDs, the segregated txinwitness data, the scriptPubKey, and the size metrics, clearly demonstrating the SegWit witness discount.

### 4. Stop the Node
Once testing is complete, safely shut down the local node:
```bash
bitcoin-cli -regtest -conf=$(pwd)/bitcoin.conf stop
```
### Key Findings: The Witness Discount
By comparing the outputs of part1.py and part2.py, this project successfully demonstrates the SegWit Witness Discount.

While the Legacy transaction has an identical physical Size and virtual vSize (225 bytes), the SegWit transaction separates the cryptographic signature into the witness structure, which receives a 75% weight discount. This results in a SegWit physical Size of 215 bytes but a significantly reduced vSize of only 134 vbytes, leading to lower transaction fees on the mainnet. Detailed stack execution proofs for both scripts can be found in Report.pdf.







