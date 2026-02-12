import os
import json
from common.db import get_connection
from etl.setup_ddl import create_schema

# --- Helper Function --- #
def get_id(table, column_map, id_column):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # 1. Try to find it first
        # avoid entry of duplicate states
        where_clause = " AND ".join([f"{k} = %s" for k in column_map.keys()])
        values = list(column_map.values())
        cursor.execute(f"SELECT {id_column} FROM {table} WHERE {where_clause}", values)
        result = cursor.fetchone()
        
        if result:
            return result[0]
        
        # 2. If not found, insert it
        cols = ", ".join(column_map.keys())
        placeholders = ", ".join(["%s"] * len(values))
        cursor.execute(f"INSERT INTO {table} ({cols}) VALUES ({placeholders})", values)
        conn.commit()
        
        # 3. Fetch it again to be 100% sure we have the correct ID
        cursor.execute(f"SELECT {id_column} FROM {table} WHERE {where_clause}", values)
        result = cursor.fetchone()
        return result[0]
    finally:
        cursor.close()
        conn.close()

# --- T : Transform --- #
def parse_path_metadata(root, file):

    path_parts = root.split(os.sep)
    
    # when it encounters the state folder it extract the state_name (metadata) form folder name
    if "state" in path_parts:
        raw_state = path_parts[path_parts.index("state") + 1]
        state_name = raw_state.replace("-", " ").title()
    else:
        state_name = "India" # Let get_id find the ID for "India"
    
    state_id = get_id("dim_state", {"state_name": state_name}, "state_id")
    
    # extracting year, quarter (metadata) 
    year = int(path_parts[-1])
    quarter = int(file.replace(".json", ""))
    time_id = get_id("dim_time", {"year": year, "quarter": quarter}, "time_id")
    
    return state_id, time_id

# --- E : Extract --- #
def extract_transactions():
    """Extracts Aggregated Transaction data."""

    base_path = os.path.join(os.getcwd(), 'data', 'aggregated', 'transaction', 'country', 'india')

    print("Processing Transactions...")

    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith(".json"):
                state_id, time_id = parse_path_metadata(root, file)
                with open(os.path.join(root, file), 'r') as f:
                    data = json.load(f)
                
                conn = get_connection()
                cursor = conn.cursor()
                # Key: data -> transactionData
                for item in data['data'].get('transactionData', []):
                    txn_type_id = get_id("dim_transaction_type", {"txn_type_name": item['name']}, "txn_type_id")
                    count = item['paymentInstruments'][0]['count']
                    amount = item['paymentInstruments'][0]['amount']
                    
                    cursor.execute("""
                        INSERT INTO fact_transactions (state_id, time_id, txn_type_id, txn_count, txn_amount)
                        VALUES (%s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE txn_count=VALUES(txn_count), txn_amount=VALUES(txn_amount)
                    """, (state_id, time_id, txn_type_id, count, amount))
                conn.commit()
                cursor.close()
                conn.close()

def extract_insurance():
    """Extracts Aggregated Insurance data."""

    base_path = os.path.join(os.getcwd(), 'data', 'aggregated', 'insurance', 'country', 'india')

    print("Processing Insurance...")
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith(".json"):
                state_id, time_id = parse_path_metadata(root, file)
                with open(os.path.join(root, file), 'r') as f:
                    data = json.load(f)
                
                conn = get_connection()
                cursor = conn.cursor()
                # Key: data -> transactionData (Insurance uses same key structure)
                for item in data['data'].get('transactionData', []):
                    count = item['paymentInstruments'][0]['count']
                    amount = item['paymentInstruments'][0]['amount']
                    cursor.execute("""
                        INSERT INTO fact_insurance (state_id, time_id, insurance_count, insurance_amount)
                        VALUES (%s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE insurance_count=VALUES(insurance_count), insurance_amount=VALUES(insurance_amount)
                    """, (state_id, time_id, count, amount))
                conn.commit()
                cursor.close()
                conn.close()

def extract_users():
    """Extracts Aggregated User data (Brand analysis)."""

    base_path = os.path.join(os.getcwd(), 'data', 'aggregated', 'user', 'country', 'india')

    print("Processing User Brands...")
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith(".json"):
                state_id, time_id = parse_path_metadata(root, file)
                with open(os.path.join(root, file), 'r') as f:
                    data = json.load(f)
                
                conn = get_connection()
                cursor = conn.cursor()
                # Key: data -> usersByDevice
                devices = data['data'].get('usersByDevice')
                if devices:
                    for device in devices:
                        brand_id = get_id("dim_brand", {"brand_name": device['brand']}, "brand_id")
                        cursor.execute("""
                            INSERT INTO fact_users (state_id, time_id, brand_id, user_count, percentage)
                            VALUES (%s, %s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE user_count=VALUES(user_count), percentage=VALUES(percentage)
                        """, (state_id, time_id, brand_id, device['count'], device['percentage'] * 100))
                conn.commit()
                cursor.close()
                conn.close()

if __name__ == "__main__":
    
    print("ETL Started..")

    # Create Databse and Schemas
    create_schema()

    # --- L : Load --- # 
    extract_transactions()
    extract_insurance()
    extract_users()
    
    print("ETL Complete Successfully for Aggregate")