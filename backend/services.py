from common.db import get_connection

# 1. Populates your dropdowns
def get_filter_data():
    conn = get_connection(); cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT DISTINCT year FROM fact_transactions ORDER BY year")
    years = [row["year"] for row in cursor.fetchall()]
    cursor.execute("SELECT DISTINCT state_name FROM fact_transactions ORDER BY state_name")
    states = [row["state_name"] for row in cursor.fetchall()]
    # Added back transaction types for the filters
    cursor.execute("SELECT DISTINCT txn_type FROM fact_transactions")
    txn_types = [row["txn_type"] for row in cursor.fetchall()]
    cursor.close(); conn.close()
    return {"years": years, "states": states, "txn_types": txn_types}

# 2. Feeds the Horizontal Bar Chart
def get_txn_per_type_in_state(year, state):
    conn = get_connection(); cursor = conn.cursor(dictionary=True)
    # No joins needed anymore!
    query = """
        SELECT txn_type as txn_type_name, txn_amount, quarter 
        FROM fact_transactions
        WHERE year = %s AND state_name = %s
    """
    cursor.execute(query, (year, state))
    results = cursor.fetchall()
    cursor.close(); conn.close()
    return {"has_data": True, "data": results} if results else {"has_data": False}

# 3. Top 10 States for the "Top Performance" page
def get_top_10_state(year):
    conn = get_connection(); cursor = conn.cursor(dictionary=True)
    query = """
        SELECT state_name, SUM(txn_amount) as total_amount 
        FROM fact_transactions 
        WHERE year = %s AND state_name != 'India' 
        GROUP BY state_name 
        ORDER BY total_amount DESC 
        LIMIT 10
    """
    cursor.execute(query, (year,))
    results = cursor.fetchall()
    cursor.close(); conn.close()
    return {"has_data": True, "data": results} if results else {"has_data": False}

# 4. Map Shading logic
def get_map_shading_data(data_type, year, quarter):
    conn = get_connection(); cursor = conn.cursor(dictionary=True)
    table = "fact_transactions" if data_type == "transaction" else "fact_insurance"
    col = "txn_count" if data_type == "transaction" else "insurance_count"
    query = f"SELECT state_name, SUM({col}) as total_val FROM {table} WHERE year = %s AND quarter = %s GROUP BY state_name"
    cursor.execute(query, (year, quarter))
    res = {row['state_name']: row['total_val'] for row in cursor.fetchall()}
    cursor.close(); conn.close()
    return res

# 5. Summaries (Transaction & Insurance)
def get_insurance_summary(state, year, quarter):
    target = "India" if state == "All India" else state
    conn = get_connection(); cursor = conn.cursor(dictionary=True)
    query = "SELECT SUM(insurance_count) as total_policies, SUM(insurance_amount) as total_premium FROM fact_insurance WHERE state_name = %s AND year = %s AND quarter = %s"
    cursor.execute(query, (target, year, quarter))
    res = cursor.fetchone()
    cursor.close(); conn.close()
    if not res or not res['total_policies']: return {"has_data": False}
    return {"has_data": True, "total_policies": int(res['total_policies']), "total_premium": float(res['total_premium']), "avg_premium": float(res['total_premium'] / res['total_policies'])}

def get_transaction_summary(state, year, quarter):
    target = "India" if state == "All India" else state
    conn = get_connection(); cursor = conn.cursor(dictionary=True)
    query = "SELECT txn_type as name, SUM(txn_count) as count, SUM(txn_amount) as amount FROM fact_transactions WHERE state_name = %s AND year = %s AND quarter = %s GROUP BY txn_type"
    cursor.execute(query, (target, year, quarter))
    rows = cursor.fetchall()
    cursor.close(); conn.close()
    if not rows: return {"has_data": False}
    tc = sum(r['count'] for r in rows); ta = sum(r['amount'] for r in rows)
    return {"has_data": True, "total_count": int(tc), "total_amount": float(ta), "avg_payment_value": float(ta/tc), "categories": rows}