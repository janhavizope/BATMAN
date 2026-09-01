import pandas as pd
import numpy as np
import random
import string
from datetime import datetime, timedelta
import ast

NUM_TRANSACTIONS = 50_000
NUM_WALLETS = 5_000
NUM_IPS = 1_000
OUTPUT_PATH = "data/dev/dev_dataset_50k.csv"

random.seed(42)
np.random.seed(42)

def random_wallet():
    return "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa" + str(random.randint(0, 999)).zfill(3)

def random_ip():
    return f"{random.randint(10,192)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"

def random_txid():
    return "".join(random.choices(string.hexdigits.lower(), k=64))

wallets = [random_wallet() for _ in range(NUM_WALLETS)]
ips = [random_ip() for _ in range(NUM_IPS)]
countries = ["US", "CN", "DE", "NL", "IN", "RU", "GB", "FR"]

rows = []
start_time = datetime(2026, 8, 24)

for i in range(NUM_TRANSACTIONS):
    ts = start_time + timedelta(seconds=random.randint(0, 30*24*3600))
    src_ip = random.choice(ips)
    dst_ip = random.choice(ips)
    input_addr = [random.choice(wallets)]
    output_addr = [random.choice(wallets)]
    input_amt = [round(random.uniform(0.001, 5.0), 6)]
    output_amt = [round(input_amt[0] - random.uniform(0.0001, 0.001), 6)]
    entity_id = f"entity_{random.randint(0, NUM_WALLETS//10)}"
    is_suspicious = random.random() < 0.02
    pattern_type = random.choice(["fan_in","fan_out","rapid_chain","burst"]) if is_suspicious else "normal"

    rows.append({
        "timestamp": ts.isoformat(),
        "src_ip": src_ip,
        "dst_ip": dst_ip,
        "src_port": random.randint(1024, 65000),
        "dst_port": 8333,
        "txid": random_txid(),
        "input_addresses[]": str(input_addr),
        "output_addresses[]": str(output_addr),
        "input_amounts[]": str(input_amt),
        "output_amounts[]": str(output_amt),
        "geo_country": random.choice(countries),
        "asn": f"AS{random.randint(1000,9999)}",
        "fee": round(random.uniform(0.00001, 0.001), 6),
        "script_type": random.choice(["P2PKH","P2WPKH","P2SH"]),
        "block_height": 800000 + i,
        "block_timestamp": ts.isoformat(),
        "connection_duration": round(random.uniform(1, 300), 2),
        "entity_id": entity_id,
        "is_suspicious": is_suspicious,
        "pattern_type": pattern_type
    })

df = pd.DataFrame(rows)

# CRITICAL FIX: quote all fields properly so list-type columns don't break CSV parsing
df.to_csv(OUTPUT_PATH, index=False, quoting=1)  # quoting=1 means QUOTE_ALL

print(f"Saved {len(df)} rows to {OUTPUT_PATH}")

# Verify it loads back correctly
check = pd.read_csv(OUTPUT_PATH)
print(f"Verified: loaded back {len(check)} rows successfully")
print(check.head(2))