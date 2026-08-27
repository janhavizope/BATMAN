#!/usr/bin/env python3
"""
generate_dev_data.py
Generates a small synthetic development dataset (~500 transactions, ~100 wallets, ~50 IPs)
representing Bitcoin transaction traffic with both normal transactions and 
suspicious transaction patterns (fan-in, fan-out, rapid transfer chains, bursts).

Labeled clearly as DEVELOPMENT DATA.
Saves to data/dev/dev_dataset.csv.
"""

import os
import json
import random
import hashlib
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Set random seed for reproducibility
random.seed(42)
np.random.seed(42)

def generate_txid():
    """Generate a mock Bitcoin-like transaction hash (64 hex characters)."""
    val = random.random().hex().encode('utf-8')
    return hashlib.sha256(val).hexdigest()

def generate_ip(pool):
    """Select a random IP from a pre-defined pool."""
    return random.choice(pool)

def generate_wallet(pool):
    """Select a random wallet address from a pre-defined pool."""
    return random.choice(pool)

def main():
    print("Generating synthetic development dataset...")
    
    # Pools
    ips = [f"192.168.1.{i}" for i in range(1, 40)] + \
          [f"10.0.0.{i}" for i in range(1, 10)] + \
          ["172.16.0.5", "172.16.0.10"] # 51 IPs
          
    wallets = [f"1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa{i:03d}" for i in range(100)] # 100 wallets
    countries = ["US", "DE", "CN", "RU", "NL", "GB", "CH", "IN", "JP", "BR"]
    asns = [f"AS{random.randint(1000, 9999)}" for _ in range(20)]
    script_types = ["P2PKH", "P2SH", "P2WPKH", "P2WSH"]
    
    # Let's initialize timestamps
    start_time = datetime(2026, 8, 24, 0, 0, 0)
    
    transactions = []
    
    # 1. Normal Transactions (~430)
    # Most transactions are single/double input/output
    print("Creating normal transactions...")
    for i in range(430):
        tx_time = start_time + timedelta(seconds=random.randint(0, 172800)) # over 2 days
        src_ip = generate_ip(ips)
        dst_ip = generate_ip(ips)
        src_port = random.randint(1024, 65535)
        dst_port = 8333 # Standard Bitcoin P2P port
        
        txid = generate_txid()
        
        # Inputs/outputs
        num_inputs = random.choices([1, 2, 3], weights=[0.8, 0.15, 0.05])[0]
        num_outputs = random.choices([1, 2], weights=[0.3, 0.7])[0] # 2 outputs represents (recipient + change)
        
        tx_inputs = [generate_wallet(wallets) for _ in range(num_inputs)]
        tx_outputs = [generate_wallet(wallets) for _ in range(num_outputs)]
        
        # amounts
        input_total = round(random.uniform(0.001, 5.0), 6)
        fee = round(input_total * random.uniform(0.0001, 0.005), 6)
        # distribute outputs
        remaining = input_total - fee
        if num_outputs == 1:
            tx_output_amounts = [round(remaining, 6)]
        else:
            out1 = round(remaining * random.uniform(0.1, 0.9), 6)
            out2 = round(remaining - out1, 6)
            tx_output_amounts = [out1, out2]
            
        tx_input_amounts = []
        # divide input amounts
        if num_inputs == 1:
            tx_input_amounts = [input_total]
        else:
            parts = np.random.dirichlet(np.ones(num_inputs)) * input_total
            tx_input_amounts = [round(x, 6) for x in parts]
            
        geo = random.choice(countries)
        asn = random.choice(asns)
        script = random.choice(script_types)
        
        block_h = 800000 + int((tx_time - start_time).total_seconds() / 600) # ~10 mins block time
        block_time = start_time + timedelta(minutes=(block_h - 800000)*10)
        
        conn_duration = round(random.uniform(0.5, 120.0), 2)
        entity_id = f"entity_{random.randint(1, 50)}"
        
        transactions.append({
            "timestamp": tx_time.isoformat(),
            "src_ip": src_ip,
            "dst_ip": dst_ip,
            "src_port": src_port,
            "dst_port": dst_port,
            "txid": txid,
            "input_addresses[]": json.dumps(tx_inputs),
            "output_addresses[]": json.dumps(tx_outputs),
            "input_amounts[]": json.dumps(tx_input_amounts),
            "output_amounts[]": json.dumps(tx_output_amounts),
            "geo_country": geo,
            "asn": asn,
            "fee": fee,
            "script_type": script,
            "block_height": block_h,
            "block_timestamp": block_time.isoformat(),
            "connection_duration": conn_duration,
            "entity_id": entity_id,
            "is_suspicious": False,
            "pattern_type": "normal"
        })
        
    # 2. Suspicious Pattern: Fan-out (~15 transactions)
    # A single wallet sends funds to many unique wallets in a short time
    print("Creating suspicious Fan-out pattern...")
    fan_out_wallet = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa_FAN_OUT_SRC"
    fan_out_ip = "192.168.1.100"
    fan_out_entity = "entity_fan_out_adversary"
    fan_out_start = start_time + timedelta(hours=12)
    
    for i in range(15):
        tx_time = fan_out_wallet_time = fan_out_start + timedelta(seconds=i * 60) # every minute
        txid = generate_txid()
        dest_wallet = f"1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa_FO_DST_{i}"
        
        input_total = 1.0
        fee = 0.0005
        output_amount = input_total - fee
        
        transactions.append({
            "timestamp": tx_time.isoformat(),
            "src_ip": fan_out_ip,
            "dst_ip": generate_ip(ips),
            "src_port": random.randint(1024, 65535),
            "dst_port": 8333,
            "txid": txid,
            "input_addresses[]": json.dumps([fan_out_wallet]),
            "output_addresses[]": json.dumps([dest_wallet]),
            "input_amounts[]": json.dumps([input_total]),
            "output_amounts[]": json.dumps([output_amount]),
            "geo_country": "RU", # Suspicious country association
            "asn": "AS6666",
            "fee": fee,
            "script_type": "P2PKH",
            "block_height": 800000 + int((tx_time - start_time).total_seconds() / 600),
            "block_timestamp": (start_time + timedelta(minutes=int((tx_time - start_time).total_seconds() / 600)*10)).isoformat(),
            "connection_duration": round(random.uniform(0.1, 5.0), 2),
            "entity_id": fan_out_entity,
            "is_suspicious": True,
            "pattern_type": "fan_out"
        })
        
    # 3. Suspicious Pattern: Fan-in (~15 transactions)
    # Many unique wallets send funds to a single wallet in a short time
    print("Creating suspicious Fan-in pattern...")
    fan_in_wallet = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa_FAN_IN_DST"
    fan_in_ip = "192.168.1.101"
    fan_in_entity = "entity_fan_in_adversary"
    fan_in_start = start_time + timedelta(hours=24)
    
    for i in range(15):
        tx_time = fan_in_start + timedelta(seconds=i * 45) # every 45s
        txid = generate_txid()
        src_wallet = f"1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa_FI_SRC_{i}"
        
        input_total = 0.5
        fee = 0.0002
        output_amount = input_total - fee
        
        transactions.append({
            "timestamp": tx_time.isoformat(),
            "src_ip": generate_ip(ips),
            "dst_ip": fan_in_ip,
            "src_port": random.randint(1024, 65535),
            "dst_port": 8333,
            "txid": txid,
            "input_addresses[]": json.dumps([src_wallet]),
            "output_addresses[]": json.dumps([fan_in_wallet]),
            "input_amounts[]": json.dumps([input_total]),
            "output_amounts[]": json.dumps([output_amount]),
            "geo_country": "CN",
            "asn": "AS8888",
            "fee": fee,
            "script_type": "P2SH",
            "block_height": 800000 + int((tx_time - start_time).total_seconds() / 600),
            "block_timestamp": (start_time + timedelta(minutes=int((tx_time - start_time).total_seconds() / 600)*10)).isoformat(),
            "connection_duration": round(random.uniform(0.1, 5.0), 2),
            "entity_id": fan_in_entity,
            "is_suspicious": True,
            "pattern_type": "fan_in"
        })
        
    # 4. Suspicious Pattern: Rapid Transfer Chain (Multi-hop) (8 transactions)
    # Wallet 0 -> Wallet 1 -> Wallet 2 -> Wallet 3 -> Wallet 4 -> Wallet 5 -> Wallet 6 -> Wallet 7
    print("Creating suspicious Rapid Transfer Chain pattern...")
    chain_wallets = [f"1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa_CHAIN_{i}" for i in range(9)]
    chain_ip = "172.16.0.200"
    chain_entity = "entity_rapid_chain_adversary"
    chain_start = start_time + timedelta(hours=36)
    
    amount = 5.0
    for i in range(8):
        tx_time = chain_start + timedelta(minutes=i * 2) # hop happens every 2 minutes
        txid = generate_txid()
        
        input_amount = amount
        fee = 0.001
        output_amount = round(input_amount - fee, 6)
        amount = output_amount # pass next amount down the chain
        
        transactions.append({
            "timestamp": tx_time.isoformat(),
            "src_ip": chain_ip,
            "dst_ip": chain_ip,
            "src_port": random.randint(1024, 65535),
            "dst_port": 8333,
            "txid": txid,
            "input_addresses[]": json.dumps([chain_wallets[i]]),
            "output_addresses[]": json.dumps([chain_wallets[i+1]]),
            "input_amounts[]": json.dumps([input_amount]),
            "output_amounts[]": json.dumps([output_amount]),
            "geo_country": "NL",
            "asn": "AS5555",
            "fee": fee,
            "script_type": "P2WPKH",
            "block_height": 800000 + int((tx_time - start_time).total_seconds() / 600),
            "block_timestamp": (start_time + timedelta(minutes=int((tx_time - start_time).total_seconds() / 600)*10)).isoformat(),
            "connection_duration": round(random.uniform(0.1, 10.0), 2),
            "entity_id": chain_entity,
            "is_suspicious": True,
            "pattern_type": "rapid_transfer"
        })
        
    # 5. Suspicious Pattern: High-frequency Burst (~25 transactions)
    # An entity/IP executes many transactions in a short interval (e.g. 1 minute)
    print("Creating suspicious Burst pattern...")
    burst_ip = "192.168.1.200"
    burst_entity = "entity_burst_adversary"
    burst_start = start_time + timedelta(hours=42)
    
    for i in range(25):
        tx_time = burst_start + timedelta(seconds=i * 2) # every 2 seconds
        txid = generate_txid()
        
        input_total = round(random.uniform(0.01, 0.1), 4)
        fee = 0.0001
        output_amount = round(input_total - fee, 4)
        
        transactions.append({
            "timestamp": tx_time.isoformat(),
            "src_ip": burst_ip,
            "dst_ip": generate_ip(ips),
            "src_port": random.randint(1024, 65535),
            "dst_port": 8333,
            "txid": txid,
            "input_addresses[]": json.dumps([generate_wallet(wallets)]),
            "output_addresses[]": json.dumps([generate_wallet(wallets)]),
            "input_amounts[]": json.dumps([input_total]),
            "output_amounts[]": json.dumps([output_amount]),
            "geo_country": "US",
            "asn": "AS7777",
            "fee": fee,
            "script_type": "P2WPKH",
            "block_height": 800000 + int((tx_time - start_time).total_seconds() / 600),
            "block_timestamp": (start_time + timedelta(minutes=int((tx_time - start_time).total_seconds() / 600)*10)).isoformat(),
            "connection_duration": round(random.uniform(0.05, 0.5), 2),
            "entity_id": burst_entity,
            "is_suspicious": True,
            "pattern_type": "burst"
        })

    # Sort transactions chronologically
    transactions.sort(key=lambda x: x["timestamp"])
    
    # Save to DataFrame
    df = pd.DataFrame(transactions)
    
    # Create target directories
    os.makedirs(os.path.join("bitcoin-monitor", "data", "dev"), exist_ok=True)
    out_path = os.path.join("bitcoin-monitor", "data", "dev", "dev_dataset.csv")
    
    df.to_csv(out_path, index=False)
    
    print(f"Generated {len(df)} transactions.")
    print(f"Labeled {df['is_suspicious'].sum()} transactions as suspicious.")
    print(df['pattern_type'].value_counts())
    print(f"Saved dataset to {out_path}")

if __name__ == "__main__":
    main()
