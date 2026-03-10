from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import json
import time

# --- Setup RPC Connection ---
rpc_user = "bitcoinrpc" 
rpc_password = "secretpassword"
rpc_port = 18443 # Regtest default port

rpc_url = f"http://{rpc_user}:{rpc_password}@127.0.0.1:{rpc_port}"
rpc = AuthServiceProxy(rpc_url)

wallet_name = "lab_wallet_final_run"

try:
    rpc.createwallet(wallet_name)
except JSONRPCException:
    try:
        rpc.loadwallet(wallet_name)
    except JSONRPCException:
        pass

rpc_wallet = AuthServiceProxy(f"{rpc_url}/wallet/{wallet_name}")

print("--- Generating Addresses ---")
addr_a = rpc_wallet.getnewaddress("A", "legacy")
addr_b = rpc_wallet.getnewaddress("B", "legacy")
addr_c = rpc_wallet.getnewaddress("C", "legacy")

print(f"Address A: {addr_a}")
print(f"Address B: {addr_b}")
print(f"Address C: {addr_c}\n")

print("--- Funding Address A ---")
rpc_wallet.generatetoaddress(101, addr_a)
print("Mined 101 blocks. Address A is funded.\n")

# ---------------------------------------------------------
# TRANSACTION 1: A -> B
# ---------------------------------------------------------
print("--- Creating TX: A -> B ---")
unspent_a = rpc_wallet.listunspent(1, 9999999, [addr_a])
if not unspent_a:
    raise Exception("No UTXOs found for A!")
utxo_a = unspent_a[0]

# THE FIX: Dynamically split whatever balance A actually has
amount_a = float(utxo_a["amount"])
send_b = round(amount_a * 0.5, 8)
change_a = round(amount_a - send_b - 0.001, 8)

inputs_ab = [{"txid": utxo_a["txid"], "vout": utxo_a["vout"]}]
outputs_ab = {addr_b: send_b, addr_a: change_a}

raw_tx_ab = rpc_wallet.createrawtransaction(inputs_ab, outputs_ab)
signed_tx_ab = rpc_wallet.signrawtransactionwithwallet(raw_tx_ab)
txid_ab = rpc_wallet.sendrawtransaction(signed_tx_ab["hex"])
print(f"TXID A -> B: {txid_ab}")

decoded_ab = rpc_wallet.decoderawtransaction(signed_tx_ab["hex"])
print("\n[Decoded A->B] ScriptPubKey for Address B:")
for vout in decoded_ab["vout"]:
    if addr_b in vout["scriptPubKey"].get("address", "") or addr_b in vout["scriptPubKey"].get("addresses", []):
        print(json.dumps(vout["scriptPubKey"], indent=2))

rpc_wallet.generatetoaddress(1, addr_a)
time.sleep(1)


# TRANSACTION 2: B -> C
print("\n--- Creating TX: B -> C ---")
unspent_b = rpc_wallet.listunspent(1, 9999999, [addr_b])
utxo_b = unspent_b[0]

# Dynamically split whatever balance B actually has
amount_b = float(utxo_b["amount"])
send_c = round(amount_b * 0.5, 8)
change_b = round(amount_b - send_c - 0.001, 8)

inputs_bc = [{"txid": utxo_b["txid"], "vout": utxo_b["vout"]}]
outputs_bc = {addr_c: send_c, addr_b: change_b}

raw_tx_bc = rpc_wallet.createrawtransaction(inputs_bc, outputs_bc)
signed_tx_bc = rpc_wallet.signrawtransactionwithwallet(raw_tx_bc)

txid_bc = rpc_wallet.sendrawtransaction(signed_tx_bc["hex"])
print(f"TXID B -> C: {txid_bc}")

decoded_bc = rpc_wallet.decoderawtransaction(signed_tx_bc["hex"])
print("\n[Decoded B->C] ScriptSig (Unlocking Script) from B:")
print(json.dumps(decoded_bc["vin"][0]["scriptSig"], indent=2))

rpc_wallet.generatetoaddress(1, addr_a)

print("\n--- Script Analysis (Part 1: Legacy P2PKH) ---")
print("Size:", decoded_bc["size"], "bytes")
print("vSize:", decoded_bc["vsize"], "vbytes")
print("Weight:", decoded_bc["weight"], "wu")
print("\nDone. Check the outputs to use in btcdeb!")