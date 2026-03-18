import os
import json
from common.db import get_connection
from etl.setup_ddl import create_schema

def parse_metadata(root, file):
    path_parts = root.split(os.sep)
    state_name = path_parts[path_parts.index("state") + 1].replace("-", " ").title() if "state" in path_parts else "India"
    year = int(path_parts[-1])
    quarter = int(file.replace(".json", ""))
    return state_name, year, quarter

def extract_transactions():
    base_path = os.path.join(os.getcwd(), 'data', 'aggregated', 'transaction', 'country', 'india')
    print("Processing Transactions...")
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith(".json"):
                state, year, qtr = parse_metadata(root, file)
                with open(os.path.join(root, file), 'r') as f:
                    data = json.load(f)
                conn = get_connection(); cursor = conn.cursor()
                for item in data['data'].get('transactionData', []):
                    cursor.execute("""
                        INSERT INTO fact_transactions (state_name, year, quarter, txn_type, txn_count, txn_amount)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE txn_count=VALUES(txn_count), txn_amount=VALUES(txn_amount)
                    """, (state, year, qtr, item['name'], item['paymentInstruments'][0]['count'], item['paymentInstruments'][0]['amount']))
                conn.commit(); cursor.close(); conn.close()

def extract_insurance():
    base_path = os.path.join(os.getcwd(), 'data', 'aggregated', 'insurance', 'country', 'india')
    print("Processing Insurance...")
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith(".json"):
                state, year, qtr = parse_metadata(root, file)
                with open(os.path.join(root, file), 'r') as f:
                    data = json.load(f)
                conn = get_connection(); cursor = conn.cursor()
                for item in data['data'].get('transactionData', []):
                    cursor.execute("""
                        INSERT INTO fact_insurance (state_name, year, quarter, insurance_count, insurance_amount)
                        VALUES (%s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE insurance_count=VALUES(insurance_count), insurance_amount=VALUES(insurance_amount)
                    """, (state, year, qtr, item['paymentInstruments'][0]['count'], item['paymentInstruments'][0]['amount']))
                conn.commit(); cursor.close(); conn.close()

def extract_users():
    base_path = os.path.join(os.getcwd(), 'data', 'aggregated', 'user', 'country', 'india')
    print("Processing Users...")
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith(".json"):
                state, year, qtr = parse_metadata(root, file)
                with open(os.path.join(root, file), 'r') as f:
                    data = json.load(f)
                devices = data['data'].get('usersByDevice')
                if devices:
                    conn = get_connection(); cursor = conn.cursor()
                    for dev in devices:
                        cursor.execute("""
                            INSERT INTO fact_users (state_name, year, quarter, brand_name, user_count, percentage)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE user_count=VALUES(user_count), percentage=VALUES(percentage)
                        """, (state, year, qtr, dev['brand'], dev['count'], dev['percentage'] * 100))
                    conn.commit(); cursor.close(); conn.close()

if __name__ == "__main__":
    create_schema()
    extract_transactions()
    extract_insurance()
    extract_users()
    print("ETL Complete.")