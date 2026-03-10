from bitcoinrpc.authproxy import AuthServiceProxy
import json
import time

RPC_USER = "bitcoinrpc"
RPC_PASSWORD = "secretpassword"

BASE_URL = f"http://{RPC_USER}:{RPC_PASSWORD}@127.0.0.1:18443"
WALLET_NAME = "segwit_lab"


def rpc_wallet():
    return AuthServiceProxy(f"{BASE_URL}/wallet/{WALLET_NAME}")


def run_part_2():

    print("\n--- Loading Wallet:", WALLET_NAME, "---")

    base_rpc = AuthServiceProxy(BASE_URL)

    wallets = base_rpc.listwallets()

    if WALLET_NAME not in wallets:
        try:
            base_rpc.createwallet(WALLET_NAME)
        except:
            base_rpc.loadwallet(WALLET_NAME)

    time.sleep(1)

    rpc = rpc_wallet()

    print("\n--- Generating Addresses ---")

    A = rpc.getnewaddress("A_prime", "p2sh-segwit")
    B = rpc.getnewaddress("B_prime", "p2sh-segwit")
    C = rpc.getnewaddress("C_prime", "p2sh-segwit")

    print("A':", A)
    print("B':", B)
    print("C':", C)

    print("\n--- Mining Blocks ---")

    miner = rpc.getnewaddress("miner", "p2sh-segwit")
    rpc.generatetoaddress(101, miner)

    print("\n--- Funding A' ---")

    fund_txid = rpc.sendtoaddress(A, 2.0)
    print("Funding TXID:", fund_txid)

    rpc.generatetoaddress(1, miner)

    print("\n--- Transaction A' -> B' ---")

    utxo_A = rpc.listunspent(1, 999, [A])[0]

    inputs_AB = [{
        "txid": utxo_A["txid"],
        "vout": utxo_A["vout"]
    }]

    outputs_AB = {B: 1.999}

    raw_AB = rpc.createrawtransaction(inputs_AB, outputs_AB)

    print("\nRaw Transaction:")
    print(raw_AB)

    decoded_AB = rpc.decoderawtransaction(raw_AB)

    print("\nDecoded Transaction:")
    print(json.dumps(decoded_AB, indent=2, default=str))

    signed_AB = rpc.signrawtransactionwithwallet(raw_AB)
    txid_AB = rpc.sendrawtransaction(signed_AB["hex"])

    print("\nBroadcasted TXID:", txid_AB)

    rpc.generatetoaddress(1, miner)

    print("\n--- Extracting scriptPubKey for B' ---")

    tx_AB_wallet = rpc.gettransaction(txid_AB)
    decoded_tx_AB = rpc.decoderawtransaction(tx_AB_wallet["hex"])

    for vout in decoded_tx_AB["vout"]:
        if vout["scriptPubKey"].get("address") == B:
            print("\nscriptPubKey ASM:", vout["scriptPubKey"]["asm"])
            print("scriptPubKey HEX:", vout["scriptPubKey"]["hex"])

    print("\n--- Transaction B' -> C' ---")

    utxo_B = rpc.listunspent(1, 999, [B])[0]

    inputs_BC = [{
        "txid": utxo_B["txid"],
        "vout": utxo_B["vout"]
    }]

    outputs_BC = {C: 1.998}

    raw_BC = rpc.createrawtransaction(inputs_BC, outputs_BC)

    signed_BC = rpc.signrawtransactionwithwallet(raw_BC)

    print("\nSigned Transaction HEX (for btcdeb):")
    print(signed_BC["hex"])

    txid_BC = rpc.sendrawtransaction(signed_BC["hex"])

    print("\nBroadcasted TXID:", txid_BC)

    rpc.generatetoaddress(1, miner)

    tx_BC_wallet = rpc.gettransaction(txid_BC)
    decoded_BC = rpc.decoderawtransaction(tx_BC_wallet["hex"])

    print("\n--- Script Analysis ---")

    print("\nSize:", decoded_BC["size"])
    print("vSize:", decoded_BC["vsize"])
    print("Weight:", decoded_BC["weight"])

    vin = decoded_BC["vin"][0]

    print("\nscriptSig:")
    print(vin.get("scriptSig", {}).get("asm", "N/A"))

    if "txinwitness" in vin:
        print("\nWitness:")
        for item in vin["txinwitness"]:
            print(item)

    vout = decoded_BC["vout"][0]

    print("\nscriptPubKey ASM:")
    print(vout["scriptPubKey"]["asm"])

    print("\nscriptPubKey HEX:")
    print(vout["scriptPubKey"]["hex"])

    print("\n--- Workflow Summary ---")

    print("Tx A' -> B' :", txid_AB)
    print("Tx B' -> C' :", txid_BC)


if __name__ == "__main__":
    run_part_2()