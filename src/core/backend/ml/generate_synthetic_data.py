"""
generate_synthetic_data.py
---------------------------
Generates synthetic Bitcoin transaction data for training an
illicit-transaction-detection ML model.

Output columns:
    txid              - unique transaction id (hash-like string)
    timestamp          - ISO datetime of the transaction
    input_address       - sending wallet address (synthetic)
    output_address      - receiving wallet address (synthetic)
    amount_btc          - transaction amount in BTC
    fee_btc             - miner fee in BTC
    num_inputs           - number of inputs in the tx
    num_outputs          - number of outputs in the tx
    block_height         - synthetic block height
    ip_address           - IP associated with the broadcasting node (synthetic)
    is_new_address_out    - 1 if output_address has never been seen before this tx
    tx_per_hour_sender    - rolling tx frequency for the sender in past hour
    is_illicit            - LABEL (1 = illicit/suspicious, 0 = legitimate)

The illicit-pattern heuristics baked in (so the label is learnable, not random):
    - Mixing-service-like behavior: many inputs -> many outputs, small amounts, high frequency
    - Rapid succession of transactions from the same address ("layering")
    - Round-number amounts sent to brand-new addresses (common in scam payouts)
    - Unusually high fees paired with unusually small amounts (obfuscation)
    - Known-bad IP ranges (simulated) reused across many different wallets
"""

import csv
import hashlib
import random
import ipaddress
from datetime import datetime, timedelta

random.seed(42)

N_ROWS = 20_000
ILLICIT_RATE = 0.12  # ~12% illicit, realistic-ish for a detection task

OUTPUT_FILE = "synthetic_bitcoin_transactions.csv"

# ---------------------------------------------------------------------------
# Helpers to generate realistic-looking synthetic values
# ---------------------------------------------------------------------------

def random_hash(prefix=""):
    raw = f"{prefix}{random.random()}{datetime.now()}".encode()
    return hashlib.sha256(raw).hexdigest()


def random_address():
    # Bitcoin-ish bech32/base58 looking address (NOT a real address format,
    # just realistic-looking synthetic data)
    charset = "123456789abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ"
    return "bc1" + "".join(random.choice(charset) for _ in range(38))


def random_ip(bad_pool=None):
    if bad_pool and random.random() < 0.5:
        return random.choice(bad_pool)
    return str(ipaddress.IPv4Address(random.randint(0, 2**32 - 1)))


def random_timestamp(start, end):
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))


# A small pool of "known bad" IPs that get reused across many wallets to
# simulate botnet / mixing-service infrastructure reuse.
BAD_IP_POOL = [random_ip() for _ in range(15)]

# A pool of addresses that will be reused as "seen before" outputs so we can
# compute a meaningful is_new_address_out feature.
SEEN_ADDRESS_POOL = [random_address() for _ in range(2000)]

# Address pools for input sources so entities have transaction histories
ILLICIT_ADDRESS_POOL = [random_address() for _ in range(150)]
LEGIT_ADDRESS_POOL = [random_address() for _ in range(1000)]

START_DATE = datetime(2025, 1, 1)
END_DATE = datetime(2025, 12, 31)


def generate_row(is_illicit: bool, address_seen_tracker: set):
    ts = random_timestamp(START_DATE, END_DATE)

    # Label noise: a small fraction of rows get features drawn from the
    # "wrong" distribution, and a small fraction of labels are flipped
    # outright. This simulates real-world messiness: not every illicit tx
    # looks obviously illicit, and not every legit tx looks clean
    # (e.g. a legit power-user with high tx frequency).
    MISLABEL_RATE = 0.04
    CROSSOVER_RATE = 0.15  # fraction of rows drawn from the "wrong" behavior profile

    behaves_illicit = is_illicit
    if random.random() < CROSSOVER_RATE:
        behaves_illicit = not is_illicit  # features come from the other class

    if behaves_illicit:
        num_inputs = random.choice([1, 1, 2, 8, 12, 20])       # mixing-like fan-in sometimes
        num_outputs = random.choice([1, 5, 10, 15, 25])         # fan-out sometimes
        amount = round(random.choice([
            random.uniform(0.001, 0.05),      # many tiny "smurfing" amounts
            random.choice([1.0, 5.0, 10.0]),  # suspicious round numbers
        ]), 8)
        fee = round(amount * random.uniform(0.015, 0.08), 8)     # elevated fee ratio
        tx_per_hour_sender = random.randint(4, 40)                # rapid-fire layering
        ip = random_ip(bad_pool=BAD_IP_POOL)
        out_addr = random_address()  # fresh address, rarely reused
        is_new = 1
    else:
        num_inputs = random.choice([1, 1, 1, 2, 3])
        num_outputs = random.choice([1, 1, 2])
        amount = round(random.uniform(0.0001, 3.0), 8)
        fee = round(amount * random.uniform(0.0005, 0.015), 8)    # normal low fee ratio
        tx_per_hour_sender = random.randint(0, 6)
        ip = random_ip()
        if random.random() < 0.6 and SEEN_ADDRESS_POOL:
            out_addr = random.choice(SEEN_ADDRESS_POOL)
            is_new = 0
        else:
            out_addr = random_address()
            is_new = 1

    # add continuous jitter on top so numeric features overlap between classes
    amount = max(0.00001, round(amount * random.uniform(0.85, 1.15), 8))
    fee = max(0.00000001, round(fee * random.uniform(0.7, 1.3), 8))
    tx_per_hour_sender = max(0, tx_per_hour_sender + random.randint(-2, 2))

    # final label noise: occasionally flip the recorded label itself
    # (e.g. mislabeled ground truth, a common real-world data quality issue)
    recorded_label = is_illicit
    if random.random() < MISLABEL_RATE:
        recorded_label = not recorded_label
    is_illicit = recorded_label

    # Select an input address from the respective pool to create history clusters
    if is_illicit:
        in_addr = random.choice(ILLICIT_ADDRESS_POOL)
    else:
        in_addr = random.choice(LEGIT_ADDRESS_POOL)

    row = {
        "txid": random_hash(in_addr),
        "timestamp": ts.isoformat(),
        "input_address": in_addr,
        "output_address": out_addr,
        "amount_btc": amount,
        "fee_btc": fee,
        "num_inputs": num_inputs,
        "num_outputs": num_outputs,
        "block_height": random.randint(870_000, 900_000),
        "ip_address": ip,
        "is_new_address_out": is_new,
        "tx_per_hour_sender": tx_per_hour_sender,
        "is_illicit": int(is_illicit),
    }
    return row


def main():
    n_illicit = int(N_ROWS * ILLICIT_RATE)
    n_legit = N_ROWS - n_illicit

    rows = []
    seen = set()
    for _ in range(n_illicit):
        rows.append(generate_row(True, seen))
    for _ in range(n_legit):
        rows.append(generate_row(False, seen))

    random.shuffle(rows)

    fieldnames = list(rows[0].keys())
    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {OUTPUT_FILE}")
    print(f"  illicit:  {n_illicit} ({n_illicit/len(rows):.1%})")
    print(f"  legit:    {n_legit} ({n_legit/len(rows):.1%})")


if __name__ == "__main__":
    main()
