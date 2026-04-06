import sqlite3
import pandas as pd
from typing import Tuple, Any

class DatabaseConnection:
    """Handles an in-memory SQLite database to test generated queries."""
    
    def __init__(self):
        # Create an in-memory persistent database across a single env instance
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self._initialize_db()

    def _initialize_db(self):
        """Populate the database with tables and sample data."""
        cursor = self.conn.cursor()
        
        # Create Sales Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                transaction_id INTEGER PRIMARY KEY,
                product_id INTEGER,
                category TEXT,
                amount REAL,
                discount REAL,
                date TEXT
            )
        ''')
        
        # Create Products Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                product_id INTEGER PRIMARY KEY,
                name TEXT,
                stock INTEGER,
                supplier TEXT
            )
        ''')
        
        # Insert initial dummy sales data
        sales_data = [
            (1, 101, 'Electronics', 1200.0, 0.1, '2023-01-15'),
            (2, 102, 'Furniture', 450.0, 0.05, '2023-01-16'),
            (3, 101, 'Electronics', 1200.0, 0.1, '2023-02-10'),
            (4, 103, 'Clothing', 50.0, 0.0, '2023-02-12'),
            (5, 104, 'Electronics', 3000.0, 0.2, '2023-03-05'), # Used for anomaly/trend tasks
        ]
        cursor.executemany('INSERT INTO sales VALUES (?,?,?,?,?,?)', sales_data)
        
        # Insert initial dummy products data
        products_data = [
            (101, 'Laptop', 50, 'Supplier A'),
            (102, 'Chair', 200, 'Supplier B'),
            (103, 'T-Shirt', 1000, 'Supplier C'),
            (104, 'High-End Server', 5, 'Supplier A'), # High-revenue, specific supplier
        ]
        cursor.executemany('INSERT INTO products VALUES (?,?,?,?)', products_data)
        self.conn.commit()

    def execute_query(self, query: str) -> Tuple[bool, Any]:
        """
        Executes a raw SQL query safely.
        Returns: Tuple of (bool success_flag, actual result or error message).
        """
        try:
            df = pd.read_sql_query(query, self.conn)
            # return as dictionary list to be serialized in JSON properly by the env
            return True, df.to_dict(orient='records')
        except Exception as e:
            return False, str(e)
            
    def get_schema(self) -> str:
        """Returns the schema description for the agent."""
        return '''
        Table: sales 
        Columns: (transaction_id INTEGER, product_id INTEGER, category TEXT, amount REAL, discount REAL, date TEXT)
        
        Table: products 
        Columns: (product_id INTEGER, name TEXT, stock INTEGER, supplier TEXT)
        '''
