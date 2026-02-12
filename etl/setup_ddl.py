from common.db import get_raw_connection
from credentials import DB_NAME

def create_schema():
    """Creates the Complete PhonePe Pulse DW schema in MySQL Server."""

    # connect without database first
    conn = get_raw_connection(database=None)
    cursor = conn.cursor()

    # create the database 
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    cursor.execute(f"USE {DB_NAME}")


    # Dimention Tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dim_state(
        state_id INT AUTO_INCREMENT PRIMARY KEY,state_name VARCHAR(100) UNIQUE
    )""")
    
    # for handling inida-level data (india = 1)
    cursor.execute("INSERT IGNORE INTO dim_state (state_name) VALUES ('India')")


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dim_time (
        time_id INT AUTO_INCREMENT PRIMARY KEY,
        year INT NOT NULL,
        quarter INT NOT NULL,
        UNIQUE(year, quarter),
        INDEX idx_time_search (year, quarter)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dim_transaction_type (
        txn_type_id INT AUTO_INCREMENT PRIMARY KEY,
        txn_type_name VARCHAR(100) UNIQUE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dim_brand (
        brand_id INT AUTO_INCREMENT PRIMARY KEY,
        brand_name VARCHAR(100) UNIQUE
    )
    """)

    # Fact Tables
    # added composite indexing (time-id -> state_id -> txn_type_id )
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fact_transactions (
        fact_id BIGINT AUTO_INCREMENT PRIMARY KEY,
        state_id INT NOT NULL,
        time_id INT NOT NULL,
        txn_type_id INT NOT NULL,
        txn_count BIGINT,
        txn_amount DECIMAL(18,2),

        UNIQUE (state_id, time_id, txn_type_id),
                   
        INDEX idx_txn_dashboard_path (time_id, state_id, txn_type_id),

        FOREIGN KEY (state_id) REFERENCES dim_state(state_id)
            ON DELETE CASCADE,
        FOREIGN KEY (time_id) REFERENCES dim_time(time_id)
            ON DELETE CASCADE,
        FOREIGN KEY (txn_type_id) REFERENCES dim_transaction_type(txn_type_id)
            ON DELETE CASCADE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fact_insurance (
        fact_id BIGINT AUTO_INCREMENT PRIMARY KEY,
        state_id INT NOT NULL,
        time_id INT NOT NULL,
        insurance_count BIGINT,
        insurance_amount DECIMAL(18,2),

        UNIQUE (state_id, time_id),
                   
        INDEX idx_ins_dashboard_path (time_id, state_id),

        FOREIGN KEY (state_id) REFERENCES dim_state(state_id)
            ON DELETE CASCADE,
        FOREIGN KEY (time_id) REFERENCES dim_time(time_id)
            ON DELETE CASCADE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fact_users (
        fact_id BIGINT AUTO_INCREMENT PRIMARY KEY,
        state_id INT NOT NULL,
        time_id INT NOT NULL,
        brand_id INT NOT NULL,
        user_count BIGINT,
        percentage DECIMAL(5,2),

        UNIQUE (state_id, time_id, brand_id),

        INDEX idx_brand_dashboard_path (time_id, state_id, brand_id),

        FOREIGN KEY (state_id) REFERENCES dim_state(state_id)
            ON DELETE CASCADE,
        FOREIGN KEY (time_id) REFERENCES dim_time(time_id)
            ON DELETE CASCADE,
        FOREIGN KEY (brand_id) REFERENCES dim_brand(brand_id)
            ON DELETE CASCADE
    )
    """)

    conn.commit()
    cursor.close()
    conn.close()

    print("Database and Tables created successfully.")
