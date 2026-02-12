import mysql.connector
from credentials import DB_USER, USER_PASSWORD, DB_NAME

# Global variable to hold the pool
_connection_pool = None

def init_pool():
    """Initializes the connection pool once."""
    global _connection_pool
    if _connection_pool is None:
        db_config = {
            "host": "localhost",
            "user": DB_USER,
            "password": USER_PASSWORD,
            "database": DB_NAME
        }
        
        # pool size = 10
        _connection_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="phonepe_pool",
            pool_size=10,
            **db_config
        )

def get_connection():
    """Fetches a connection from the pool."""
    if _connection_pool is None:
        init_pool()
    return _connection_pool.get_connection()

# for creating schema in database
def get_raw_connection(database=None):
    config = {
        "host": "localhost",
        "user": DB_USER,
        "password": USER_PASSWORD
    }
    if database:
        config["database"] = database
    return mysql.connector.connect(**config)
