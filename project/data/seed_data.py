"""
Seed script for Hindsight Memory Bank.
Loads realistic infrastructure incidents, failed commands, and postmortem lessons.
Run this script to initialize or reset the Hindsight Memory Bank.
"""

import json
import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.hindsight_memory import hindsight_bank
from backend.models import RetainPayload

def seed_database():
    interactions_path = os.path.join(os.path.dirname(__file__), "interactions.json")
    if not os.path.exists(interactions_path):
        print(f"Error: {interactions_path} not found.")
        return

    with open(interactions_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    print(f"[*] Starting Hindsight Memory Bank Seeding...")
    print(f"[*] Target Memory Bank: {hindsight_bank.memory_bank_id}")
    print(f"[*] Total Incident Records to Process: {len(records)}")

    success_count = 0
    for record in records:
        try:
            payload = RetainPayload(
                customer_id=record["customer_id"],
                customer_name=record["customer_name"],
                incident_id=record["incident_id"],
                service=record["service"],
                symptom=record["symptom"],
                naive_attempt=record.get("naive_attempt", ""),
                outcome_of_naive_attempt=record.get("outcome_of_naive_attempt", ""),
                verified_remediation=record["verified_remediation"],
                rule_learned=record["rule_learned"],
                memory_type=record.get("memory_type", "INCIDENT_RESOLUTION"),
                confidence=record.get("confidence", 0.95)
            )
            hindsight_bank.retain(payload)
            success_count += 1
            print(f"  [+] Retained {record['incident_id']} - {record['service']}")
        except Exception as e:
            print(f"  [-] Failed to retain record {record.get('id')}: {e}")

    print(f"\n[✓] Seeding Complete! {success_count} records active in Hindsight Memory Bank.")

if __name__ == "__main__":
    seed_database()
