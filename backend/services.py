# for SQL query logic
import mysql.connector
from common.db import get_connection, DB_NAME

# fetch the required data for filter
def get_filter_data():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # years
    cursor.execute("SELECT DISTINCT year FROM dim_time ORDER BY year")
    years = [row["year"] for row in cursor.fetchall()]

    # states
    cursor.execute("SELECT state_name FROM dim_state ORDER BY state_name")
    states = [row["state_name"] for row in cursor.fetchall()]

    # txn catrgories
    cursor.execute("SELECT txn_type_name FROM dim_transaction_type")
    txn_type = [row["txn_type_name"] for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    return {"years": years, "states": states, "txn_type": txn_type}


# Insurance query
def get_insurance_summary(state, year, quarter):
    # Map frontend "All India" to database "India"
    # to avoid empty results from WHERE s.state_name = %s
    target_state = "India" if state == "All India" else state

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Optimization: The query filters using the unique constraints
    # and indexes you defined in setup_ddl.py
    query = """
    SELECT
        COALESCE(SUM(f.insurance_count), 0) AS total_policies,
        COALESCE(SUM(f.insurance_amount), 0) AS total_premium,
        CASE 
            WHEN SUM(f.insurance_count) > 0 
            THEN SUM(f.insurance_amount) / SUM(f.insurance_count)
            ELSE 0
        END AS avg_premium
    FROM fact_insurance f
    INNER JOIN dim_state s ON f.state_id = s.state_id
    INNER JOIN dim_time t ON f.time_id = t.time_id
    WHERE s.state_name = %s
      AND t.year = %s
      AND t.quarter = %s
    """

    params = [target_state, year, quarter]

    try:
        cursor.execute(query, params)
        result = cursor.fetchone()

        # Check if any actual numeric data was returned
        if not result or result["total_policies"] == 0:
            return {"has_data": False, "message": "No data found"}

        return {
            "has_data": True,
            "total_policies": int(result["total_policies"]),
            "total_premium": float(result["total_premium"]),
            "avg_premium": float(result["avg_premium"]),
        }
    finally:
        cursor.close()
        conn.close()


def get_transaction_summary(state, year, quarter):
    # Map frontend "All India" to database "India"
    target_state = "India" if state == "All India" else state

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # This query gets the count and amount for EACH transaction type
    query = """
    SELECT
        d.txn_type_name,
        SUM(f.txn_count) AS type_count,
        SUM(f.txn_amount) AS type_amount
    FROM fact_transactions f
    INNER JOIN dim_state s ON f.state_id = s.state_id
    INNER JOIN dim_time t ON f.time_id = t.time_id
    INNER JOIN dim_transaction_type d ON f.txn_type_id = d.txn_type_id
    WHERE s.state_name = %s
      AND t.year = %s
      AND t.quarter = %s
    GROUP BY d.txn_type_name
    """

    try:
        cursor.execute(query, [target_state, year, quarter])
        rows = cursor.fetchall()

        if not rows:
            return {"has_data": False}

        # Calculate Grand Totals in Python from the grouped rows
        total_count = sum(row["type_count"] for row in rows)
        total_amount = sum(row["type_amount"] for row in rows)
        avg_value = total_amount / total_count if total_count > 0 else 0

        return {
            "has_data": True,
            "total_count": int(total_count),
            "total_amount": float(total_amount),
            "avg_payment_value": float(avg_value),
            "categories": [
                {
                    "name": row["txn_type_name"],
                    "count": int(row["type_count"]),
                    "amount": float(row["type_amount"]),
                }
                for row in rows
            ],
        }
    finally:
        cursor.close()
        conn.close()


# Transcation top 10 state per txn_type category
def get_top_10_state_per_type(year, quarter):
    conn = None
    try:
        conn = get_connection()

        # dictionary=True makes results accessible by column name: row['state_name']
        cursor = conn.cursor(dictionary=True)

        query = """
        WITH ranked_txns AS (
            SELECT 
                s.state_name, 
                f.txn_amount, 
                d.txn_type_name,
                ROW_NUMBER() OVER(
                    PARTITION BY d.txn_type_name 
                    ORDER BY f.txn_amount DESC
                ) AS rank_no
            FROM fact_transactions f
            JOIN dim_transaction_type d USING (txn_type_id) 
            JOIN dim_state s USING (state_id)
            JOIN dim_time t USING (time_id)
            WHERE t.year = %s AND t.quarter = %s
        )
        SELECT state_name, txn_amount, txn_type_name, rank_no
        FROM ranked_txns
        WHERE rank_no <= 10
        ORDER BY txn_type_name, rank_no;
        """

        cursor.execute(query, (year, quarter))
        results = cursor.fetchall()  # Get all top 10 per category

        if not results:
            return {"has_data": False, "message": "No data found"}

        return {"has_data": True, "data": results}  # Return the list of records

    except mysql.connector.Error as err:
        print(f"SQL Error: {err}")
        return {"has_data": False, "message": "A database error occurred."}

    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


# Transaction Top 10 states per year
def get_top_10_state(year):
    conn = None
    try:
        conn = get_connection()

        # dictionary=True makes results accessible by column name: row['state_name']
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT SUM(txn_amount) AS total_amount, state_name FROM fact_transactions
        JOIN dim_state USING (state_id)
        JOIN dim_time USING(time_id)
        WHERE year = %s AND state_id > 1
        GROUP BY state_name
        ORDER BY AVG(txn_count) DESC
        LIMIT 10;
        """

        cursor.execute(query, (year,))
        results = cursor.fetchall()  # Get all top 10 per category

        if not results:
            return {"has_data": False, "message": "No data found"}

        return {"has_data": True, "data": results}  # Return the list of records

    except mysql.connector.Error as err:
        print(f"SQL Error: {err}")
        return {"has_data": False, "message": "A database error occurred."}

    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


# Bar chart per year for every category
def get_txn_per_type_in_state(year, state):
    conn = None
    try:
        conn = get_connection()

        # dictionary=True makes results accessible by column name: row['state_name']
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT txn_type_name, txn_amount, quarter, 
                ROW_NUMBER() OVER(PARTITION BY quarter ORDER BY txn_amount DESC) AS rank_no
        FROM fact_transactions
        JOIN dim_state USING (state_id)
        JOIN dim_time USING(time_id)
        JOIN dim_transaction_type USING (txn_type_id)
        WHERE year = %s AND state_name = %s;
        """

        cursor.execute(query, (year,state))
        results = cursor.fetchall()  # Get all top 10 per category

        if not results:
            return {"has_data": False, "message": "No data found"}

        return {"has_data": True, "data": results}  # Return the list of records

    except mysql.connector.Error as err:
        print(f"SQL Error: {err}")
        return {"has_data": False, "message": "A database error occurred."}

    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


def get_map_shading_data(data_type, year, quarter):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Logic: Select totals for ALL states to color the whole map
    table = "fact_transactions" if data_type == "transaction" else "fact_insurance"
    column = "txn_count" if data_type == "transaction" else "policy_count"
    
    query = f"""
        SELECT s.state_name, SUM(f.{column}) as total_val 
        FROM {table} f
        JOIN dim_state s USING (state_id)
        JOIN dim_time t USING (time_id)
        WHERE t.year = %s AND t.quarter = %s
        GROUP BY s.state_name
    """
    
    cursor.execute(query, (year, quarter))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # Return a dictionary for fast lookup in JS: {"Bihar": 100, "Goa": 50...}
    return {row['state_name']: row['total_val'] for row in results}