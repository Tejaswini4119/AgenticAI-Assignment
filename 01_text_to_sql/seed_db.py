"""
Builds experiments/01_text_to_sql/company.db, a small SQLite database with
sample data, if it doesn't already exist. Run directly to force a rebuild.
"""
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "company.db")

CUSTOMERS = [
    (1, "Ava Martinez", "ava.martinez@example.com", "Austin", "2023-02-14"),
    (2, "Liam Chen", "liam.chen@example.com", "Seattle", "2023-05-03"),
    (3, "Sofia Rossi", "sofia.rossi@example.com", "Boston", "2023-06-21"),
    (4, "Noah Patel", "noah.patel@example.com", "Austin", "2023-08-09"),
    (5, "Mia Kowalski", "mia.kowalski@example.com", "Chicago", "2024-01-17"),
    (6, "Ethan Wright", "ethan.wright@example.com", "Seattle", "2024-03-30"),
]

PRODUCTS = [
    (1, "Wireless Mouse", "Electronics", 24.99, 150),
    (2, "Mechanical Keyboard", "Electronics", 89.99, 60),
    (3, "USB-C Hub", "Electronics", 39.50, 90),
    (4, "Deep Work", "Books", 18.00, 40),
    (5, "Atomic Habits", "Books", 16.50, 75),
    (6, "Standing Desk", "Furniture", 249.00, 20),
    (7, "Ergonomic Chair", "Furniture", 189.00, 15),
]

ORDERS = [
    (1, 1, "2024-04-01", "delivered"),
    (2, 2, "2024-04-03", "delivered"),
    (3, 1, "2024-04-10", "shipped"),
    (4, 3, "2024-04-12", "delivered"),
    (5, 4, "2024-04-15", "cancelled"),
    (6, 5, "2024-05-01", "delivered"),
    (7, 2, "2024-05-05", "pending"),
    (8, 6, "2024-05-08", "delivered"),
]

ORDER_ITEMS = [
    (1, 1, 1, 2, 24.99),
    (2, 1, 4, 1, 18.00),
    (3, 2, 2, 1, 89.99),
    (4, 3, 3, 1, 39.50),
    (5, 4, 5, 3, 16.50),
    (6, 5, 6, 1, 249.00),
    (7, 6, 2, 1, 89.99),
    (8, 6, 1, 1, 24.99),
    (9, 7, 7, 1, 189.00),
    (10, 8, 4, 2, 18.00),
    (11, 8, 5, 1, 16.50),
]

DEPARTMENTS = [
    (1, "Sales"),
    (2, "Engineering"),
    (3, "Support"),
]

EMPLOYEES = [
    (1, "Grace Lee", "Sales Rep", 62000.0, 1),
    (2, "Marcus Johnson", "Software Engineer", 118000.0, 2),
    (3, "Priya Nair", "Support Specialist", 54000.0, 3),
    (4, "Diego Alvarez", "Sales Manager", 88000.0, 1),
]

SCHEMA = """
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    city TEXT,
    signup_date TEXT
);

CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT,
    price REAL,
    stock INTEGER
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    order_date TEXT,
    status TEXT
);

CREATE TABLE order_items (
    id INTEGER PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER,
    unit_price REAL
);

CREATE TABLE departments (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    title TEXT,
    salary REAL,
    department_id INTEGER REFERENCES departments(id)
);
"""


def build(force: bool = False):
    if force and os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    if os.path.exists(DB_PATH):
        return DB_PATH

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.executescript(SCHEMA)
    cur.executemany("INSERT INTO customers VALUES (?,?,?,?,?)", CUSTOMERS)
    cur.executemany("INSERT INTO products VALUES (?,?,?,?,?)", PRODUCTS)
    cur.executemany("INSERT INTO orders VALUES (?,?,?,?)", ORDERS)
    cur.executemany("INSERT INTO order_items VALUES (?,?,?,?,?)", ORDER_ITEMS)
    cur.executemany("INSERT INTO departments VALUES (?,?)", DEPARTMENTS)
    cur.executemany("INSERT INTO employees VALUES (?,?,?,?,?)", EMPLOYEES)
    conn.commit()
    conn.close()
    return DB_PATH


if __name__ == "__main__":
    path = build(force=True)
    print(f"Rebuilt sample database at {path}")
