"""
DEVELOPMENT DATA GENERATOR
Generates a synthetic cryptocurrency/Bitcoin-like transaction dataset for development and testing.
THIS IS NOT PRODUCTION DATA. All entities, transactions, and patterns are fabricated.

Schema:
    timestamp, src_ip, dst_ip, src_port, dst_port, txid, input_addresses[],
    output_addresses[], input_amounts[], output_amounts[], geo_country, asn, fee,
    script_type, block_height, block_timestamp, connection_duration, entity_id,
    is_suspicious, pattern_type
"""

import csv
import random
import uuid
import hashlib
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ──────────────────────────────────────────────────────────────────────
# CONFIGURABLE VARIABLES — adjust these to scale the dataset
# ──────────────────────────────────────────────────────────────────────
NUM_TRANSACTIONS = 50_000
NUM_WALLETS = 5_000
NUM_IPS = 1_000
SUSPICIOUS_FRACTION = 0.02          # ~2% of wallets flagged suspicious
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "dev"
OUTPUT_FILE = OUTPUT_DIR / "dev_dataset_50k.csv"

# Country / ASN pools for realistic-ish values
COUNTRIES = [
    "US", "CA", "GB", "DE", "FR", "JP", "AU", "BR", "IN", "RU",
    "NG", "KR", "CN", "NL", "SE", "CH", "UA", "TR", "ID", "MX",
]
COUNTRY_WEIGHTS = [
    0.15, 0.08, 0.10, 0.09, 0.07, 0.06, 0.05, 0.04, 0.04, 0.03,
    0.03, 0.03, 0.03, 0.03, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02,
]
ASNS = [f"AS{random.randint(1000, 99999)}" for _ in range(200)]
SCRIPT_TYPES = ["p2pkh", "p2sh", "p2wpkh", "p2wsh", "p2tr", "op_return", "multisig"]

# ──────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ──────────────────────────────────────────────────────────────────────

def make_txid():
    raw = uuid.uuid4().hex
    return hashlib.sha256(raw.encode()).hexdigest()[:64]


def make_ip(ips):
    if ips:
        return random.choice(ips)
    a, b, c, d = (random.randint(1, 254) for _ in range(4))
    return f"{a}.{b}.{c}.{d}"


def make_btc_amount(is_large=False):
    if is_large:
        return round(random.uniform(50, 500), 8)
    return round(random.expovariate(20.0), 8)


def make_port():
    return random.randint(1024, 65535)


def make_addr(wallets):
    w = random.choice(wallets)
    raw = f"{w}-{uuid.uuid4().hex[:8]}"
    return hashlib.sha1(raw.encode()).hexdigest()[:34]


# ──────────────────────────────────────────────────────────────────────
# BUILD WALLET & IP POOLS
# ──────────────────────────────────────────────────────────────────────
wallets = [f"wallet_{i:05d}" for i in range(NUM_WALLETS)]
ips = [f"ip_{i:04d}" for i in range(NUM_IPS)]

# Mark suspicious wallets (1-2%)
num_suspicious = max(1, int(NUM_WALLETS * SUSPICIOUS_FRACTION))
suspicious_wallets = set(random.sample(wallets, num_suspicious))

# Assign persistent country/ASN per IP for realism
ip_country = {ip: random.choices(COUNTRIES, weights=COUNTRY_WEIGHTS, k=1)[0] for ip in ips}
ip_asn = {ip: random.choice(ASNS) for ip in ips}

# ──────────────────────────────────────────────────────────────────────
# GENERATE TRANSACTIONS
# ──────────────────────────────────────────────────────────────────────
base_time = datetime(2024, 1, 1, 0, 0, 0)
rows = []

for i in range(NUM_TRANSACTIONS):
    ts = base_time + timedelta(seconds=random.randint(0, 365 * 24 * 3600))
    src_ip = make_ip(ips)
    dst_ip = make_ip(ips)

    # Pick wallets for inputs / outputs
    num_inputs = random.randint(1, 5)
    num_outputs = random.randint(1, 5)
    in_wallets = random.choices(wallets, k=num_inputs)
    out_wallets = random.choices(wallets, k=num_outputs)
    in_addrs = [make_addr(w) for w in in_wallets]
    out_addrs = [make_addr(w) for w in out_wallets]
    in_amounts = [make_btc_amount() for _ in range(num_inputs)]
    out_amounts = [make_btc_amount() for _ in range(num_outputs)]

    is_suspicious = False
    pattern_type = "none"

    # Decide if this tx involves suspicious wallets
    involved_wallets = set(in_wallets + out_wallets)
    suspicious_overlap = involved_wallets & suspicious_wallets

    if suspicious_overlap and random.random() < 0.6:
        is_suspicious = True
        pattern_type = random.choice([
            "fan_in", "fan_out", "rapid_chain",
            "high_frequency_burst", "unusual_amount", "ip_wallet_repeat",
        ])

    # ── Pattern-specific overrides ──────────────────────────────────
    if is_suspicious and pattern_type == "fan_in":
        # Many small inputs → one output
        sw = list(suspicious_overlap)[0]
        num_inputs = random.randint(8, 15)
        in_wallets = [sw] * num_inputs
        in_addrs = [make_addr(sw) for _ in range(num_inputs)]
        in_amounts = [round(random.uniform(0.001, 0.01), 8) for _ in range(num_inputs)]
        out_wallets = [sw]
        out_addrs = [make_addr(sw)]
        out_amounts = [round(sum(in_amounts) * 0.999, 8)]

    elif is_suspicious and pattern_type == "fan_out":
        # One input → many outputs
        sw = list(suspicious_overlap)[0]
        num_outputs = random.randint(10, 20)
        in_wallets = [sw]
        in_addrs = [make_addr(sw)]
        in_amounts = [round(random.uniform(10, 100), 8)]
        out_wallets = [sw] * num_outputs
        out_addrs = [make_addr(sw) for _ in range(num_outputs)]
        out_amounts = [round(in_amounts[0] / num_outputs * 0.999, 8)] * num_outputs

    elif is_suspicious and pattern_type == "rapid_chain":
        # Small amount, short connection
        sw = list(suspicious_overlap)[0]
        in_wallets = [sw]
        out_wallets = [sw]
        in_addrs = [make_addr(sw)]
        out_addrs = [make_addr(sw)]
        in_amounts = [round(random.uniform(0.0001, 0.005), 8)]
        out_amounts = [round(in_amounts[0] * 0.999, 8)]

    elif is_suspicious and pattern_type == "high_frequency_burst":
        sw = list(suspicious_overlap)[0]
        ts = base_time + timedelta(seconds=random.randint(0, 3600))
        in_wallets = [sw]
        out_wallets = [random.choice(wallets)]
        in_addrs = [make_addr(sw)]
        out_addrs = [make_addr(out_wallets[0])]
        in_amounts = [round(random.uniform(0.01, 1), 8)]
        out_amounts = [round(in_amounts[0] * 0.999, 8)]

    elif is_suspicious and pattern_type == "unusual_amount":
        sw = list(suspicious_overlap)[0]
        in_wallets = [sw]
        out_wallets = [sw]
        in_addrs = [make_addr(sw)]
        out_addrs = [make_addr(sw)]
        in_amounts = [round(random.uniform(500, 21_000_000), 8)]
        out_amounts = [round(in_amounts[0] * 0.999, 8)]

    elif is_suspicious and pattern_type == "ip_wallet_repeat":
        sw = list(suspicious_overlap)[0]
        src_ip = ips[0]
        dst_ip = ips[1]
        in_wallets = [sw]
        out_wallets = [random.choice(wallets)]
        in_addrs = [make_addr(sw)]
        out_addrs = [make_addr(out_wallets[0])]
        in_amounts = [make_btc_amount()]
        out_amounts = [round(in_amounts[0] * 0.999, 8)]

    # ── Assemble row ────────────────────────────────────────────────
    row = {
        "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "src_ip": src_ip,
        "dst_ip": dst_ip,
        "src_port": make_port(),
        "dst_port": random.choice([8333, 8332, 18333, 18332, 8080]),
        "txid": make_txid(),
        "input_addresses": "|".join(in_addrs),
        "output_addresses": "|".join(out_addrs),
        "input_amounts": "|".join(str(a) for a in in_amounts),
        "output_amounts": "|".join(str(a) for a in out_amounts),
        "geo_country": ip_country.get(src_ip, "US"),
        "asn": ip_asn.get(src_ip, "AS1000"),
        "fee": round(random.uniform(0.00001, 0.001), 8),
        "script_type": random.choice(SCRIPT_TYPES),
        "block_height": random.randint(700_000, 900_000),
        "block_timestamp": (ts + timedelta(seconds=random.randint(30, 3600))).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),
        "connection_duration": round(random.uniform(0.01, 120), 2),
        "entity_id": in_wallets[0] if in_wallets else "",
        "is_suspicious": int(is_suspicious),
        "pattern_type": pattern_type,
    }
    rows.append(row)

# ──────────────────────────────────────────────────────────────────────
# WRITE CSV
# ──────────────────────────────────────────────────────────────────────
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FIELDNAMES = [
    "timestamp", "src_ip", "dst_ip", "src_port", "dst_port", "txid",
    "input_addresses", "output_addresses", "input_amounts", "output_amounts",
    "geo_country", "asn", "fee", "script_type", "block_height",
    "block_timestamp", "connection_duration", "entity_id",
    "is_suspicious", "pattern_type",
]

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    # Header comment for provenance
    f.write("# DEV DATA - synthetic dataset for development/testing only - NOT PRODUCTION\n")
    f.write(
        f"# Generated: {datetime.now(timezone.utc).isoformat()}  |  "
        f"Transactions: {NUM_TRANSACTIONS}  |  Wallets: {NUM_WALLETS}  |  IPs: {NUM_IPS}\n"
    )

    writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
    writer.writeheader()
    writer.writerows(rows)

# ── Summary stats ────────────────────────────────────────────────────
sus_count = sum(1 for r in rows if r["is_suspicious"])
pattern_counts = {}
for r in rows:
    if r["is_suspicious"]:
        p = r["pattern_type"]
        pattern_counts[p] = pattern_counts.get(p, 0) + 1

print(f"[DEV] Dataset written -> {OUTPUT_FILE}")
print(f"[DEV] Total rows:     {NUM_TRANSACTIONS}")
print(f"[DEV] Wallets used:   {NUM_WALLETS}")
print(f"[DEV] IPs used:       {NUM_IPS}")
print(f"[DEV] Suspicious:     {sus_count} ({sus_count / NUM_TRANSACTIONS * 100:.2f}%)")
print(f"[DEV] Pattern breakdown:")
for p, c in sorted(pattern_counts.items(), key=lambda x: -x[1]):
    print(f"       {p:24s}  {c}")
