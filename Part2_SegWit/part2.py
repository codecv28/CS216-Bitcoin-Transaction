# Part 2 P2SH-SegWit transactions
# A' -> B' -> C'

from bitcoinrpc.authproxy import AuthServiceProxy
import json

# Connection configuration
RPC_USER = "bitcoinrpc"
RPC_PASSWORD = "secretpassword"
RPC_URL = f"http://{RPC_USER}:{RPC_PASSWORD}@127.0.0.1:18443"

rpc = AuthServiceProxy(RPC_URL)

def run_part_2():
    wallet_name = "segwit_lab"
    print(f"--- Loading Wallet: {wallet_name} ---")
    try:
        rpc.createwallet(wallet_name)
    except Exception as e:
        # If the wallet already exists, it might throw an error. We can load it.
        try:
            rpc.loadwallet(wallet_name)
        except:
            pass # Already loaded

    # 1. Generate P2SH-SegWit addresses A', B', and C'
    print("\n--- Generating Addresses ---")
    A = rpc.getnewaddress("A_prime", "p2sh-segwit")
    B = rpc.getnewaddress("B_prime", "p2sh-segwit")
    C = rpc.getnewaddress("C_prime", "p2sh-segwit")
    
    print(f"Address A': {A}")
    print(f"Address B': {B}")
    print(f"Address C': {C}")

    # Fund A'
    print("\n--- Funding Address A' ---")
    miner = rpc.getnewaddress("miner", "p2sh-segwit")
    rpc.generatetoaddress(101, miner)
    fund_txid = rpc.sendtoaddress(A, 2.0)
    print(f"Funded A' with txid: {fund_txid}")
    rpc.generatetoaddress(1, miner) # Confirm the funding tx

    # 2. Transaction A' -> B'
    print("\n--- Creating Transaction A' -> B' ---")
    utxo_A = rpc.listunspent(1, 999, [A])[0]
    inputs_AB = [{"txid": utxo_A['txid'], "vout": utxo_A['vout']}]
    outputs_AB = {B: 1.999} # 0.001 fee
    
    raw_AB = rpc.createrawtransaction(inputs_AB, outputs_AB)
    
    # Decode and extract challenge script (scriptPubKey) for B'
    decoded_AB = rpc.decoderawtransaction(raw_AB)
    
    # Sign and broadcast
    signed_AB = rpc.signrawtransactionwithwallet(raw_AB)
    txid_AB = rpc.sendrawtransaction(signed_AB['hex'])
    print(f"Transaction A' -> B' Broadcasted. TXID: {txid_AB}")
    
    # Confirm it
    rpc.generatetoaddress(1, miner)

    # Decode again from network to show locking script (Challenge) on B'
    net_tx_AB = rpc.getrawtransaction(txid_AB, True)
    for vout in net_tx_AB['vout']:
        # Find the output that went to B'
        if vout['scriptPubKey'].get('address') == B:
            print(f"Challenge Script B' (Hex): {vout['scriptPubKey']['hex']}")
            print(f"Challenge Script B' (ASM): {vout['scriptPubKey']['asm']}")

    # 3. Transaction B' -> C'
    print("\n--- Creating Transaction B' -> C' ---")
    utxo_B = rpc.listunspent(1, 999, [B])[0]
    inputs_BC = [{"txid": utxo_B['txid'], "vout": utxo_B['vout']}]
    outputs_BC = {C: 1.998} # 0.001 fee
    
    raw_BC = rpc.createrawtransaction(inputs_BC, outputs_BC)
    signed_BC = rpc.signrawtransactionwithwallet(raw_BC)
    txid_BC = rpc.sendrawtransaction(signed_BC['hex'])
    print(f"Transaction B' -> C' Broadcasted. TXID: {txid_BC}")
    
    # Confirm it
    rpc.generatetoaddress(1, miner)

    # 4. Analyze scripts and mechanisms
    decoded_BC = rpc.getrawtransaction(txid_BC, True)
    
    print("\n--- Script Analysis (Part 2: P2SH-SegWit) ---")
    print(f"TXID: {txid_BC}")
    print(f"Size: {decoded_BC['size']} bytes")
    print(f"vSize: {decoded_BC['vsize']} vbytes")
    print(f"Weight: {decoded_BC['weight']} wu")
    
    # Unlocking mechanism: scriptSig (starts with push of redeemScript) + txinwitness
    vin = decoded_BC['vin'][0]
    print("\nUNLOCKING MECHANISM:")
    print(f"scriptSig (ASM): {vin.get('scriptSig', {}).get('asm', 'N/A')}")
    print(f"scriptSig (Hex): {vin.get('scriptSig', {}).get('hex', 'N/A')}")
    if 'txinwitness' in vin:
        print("Witness Data (Signatures/PubKey):")
        for i, item in enumerate(vin['txinwitness']):
            print(f"  Item {i}: {item}")
    
    # Locking mechanism: scriptPubKey of C'
    vout = decoded_BC['vout'][0]  # Assuming first output is C'
    print("\nLOCKING MECHANISM:")
    print(f"scriptPubKey (ASM): {vout.get('scriptPubKey', {}).get('asm', 'N/A')}")
    print(f"scriptPubKey (Hex): {vout.get('scriptPubKey', {}).get('hex', 'N/A')}")
    
    print("\nWorkflow summary for the report:")
    print(f"1. Tx A' -> B': TxID {txid_AB}")
    print(f"2. Tx B' -> C': TxID {txid_BC} (spends UTXO from B')")

if __name__ == "__main__":
    run_part_2()