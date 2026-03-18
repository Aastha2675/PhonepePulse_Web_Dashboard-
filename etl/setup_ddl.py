from common.db import get_raw_connection
from credentials import DB_NAME

def create_schema():
    conn = get_raw_connection(database=None)
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    cursor.execute(f"USE {DB_NAME}")

    # Flat Transactions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fact_transactions (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        state_name VARCHAR(100),
        year INT,
        quarter INT,
        txn_type VARCHAR(100),
        txn_count BIGINT,
        txn_amount DECIMAL(18,2),
        UNIQUE (state_name, year, quarter, txn_type),
        INDEX idx_lookup (year, quarter, state_name)
    )""")

    # Flat Insurance Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fact_insurance (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        state_name VARCHAR(100),
        year INT,
        quarter INT,
        insurance_count BIGINT,
        insurance_amount DECIMAL(18,2),
        UNIQUE (state_name, year, quarter),
        INDEX idx_lookup (year, quarter, state_name)
    )""")

    # Flat Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fact_users (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        state_name VARCHAR(100),
        year INT,
        quarter INT,
        brand_name VARCHAR(100),
        user_count BIGINT,
        percentage DECIMAL(5,2),
        UNIQUE (state_name, year, quarter, brand_name)
    )""")

    conn.commit()
    cursor.close()
    conn.close()
    print("Flat Schema created successfully.")