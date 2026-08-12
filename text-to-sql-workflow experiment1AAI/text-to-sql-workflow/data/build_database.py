"""
Builds a small sample SQLite database (a fictional retail company:
departments, employees, customers, products, orders, order_items).

Run:
    python data/build_database.py
"""
import os
import random
import sqlite3
from datetime import datetime, timedelta

from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)

DB_PATH = os.path.join(os.path.dirname(__file__), "company.db")

SCHEMA_SQL = """
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS departments;

CREATE TABLE departments (
    department_id   INTEGER PRIMARY KEY,
    name            TEXT NOT NULL,
    location        TEXT NOT NULL
);

CREATE TABLE employees (
    employee_id     INTEGER PRIMARY KEY,
    first_name      TEXT NOT NULL,
    last_name       TEXT NOT NULL,
    email           TEXT NOT NULL,
    department_id   INTEGER NOT NULL,
    hire_date       TEXT NOT NULL,
    salary          REAL NOT NULL,
    manager_id      INTEGER,
    FOREIGN KEY (department_id) REFERENCES departments(department_id),
    FOREIGN KEY (manager_id) REFERENCES employees(employee_id)
);

CREATE TABLE customers (
    customer_id     INTEGER PRIMARY KEY,
    first_name      TEXT NOT NULL,
    last_name       TEXT NOT NULL,
    email           TEXT NOT NULL,
    city            TEXT NOT NULL,
    country         TEXT NOT NULL,
    signup_date     TEXT NOT NULL
);

CREATE TABLE products (
    product_id      INTEGER PRIMARY KEY,
    name            TEXT NOT NULL,
    category        TEXT NOT NULL,
    unit_price      REAL NOT NULL,
    stock_quantity  INTEGER NOT NULL
);

CREATE TABLE orders (
    order_id        INTEGER PRIMARY KEY,
    customer_id     INTEGER NOT NULL,
    employee_id     INTEGER NOT NULL,
    order_date      TEXT NOT NULL,
    status          TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

CREATE TABLE order_items (
    order_item_id   INTEGER PRIMARY KEY,
    order_id        INTEGER NOT NULL,
    product_id      INTEGER NOT NULL,
    quantity        INTEGER NOT NULL,
    unit_price      REAL NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
"""

DEPARTMENTS = [
    ("Sales", "New York"),
    ("Engineering", "San Francisco"),
    ("Marketing", "Chicago"),
    ("Support", "Austin"),
    ("HR", "Boston"),
]

CATEGORIES = ["Electronics", "Home & Kitchen", "Sports", "Books", "Toys", "Apparel"]
STATUSES = ["pending", "shipped", "delivered", "cancelled"]


def build():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.executescript(SCHEMA_SQL)

    # departments
    cur.executemany(
        "INSERT INTO departments (name, location) VALUES (?, ?)", DEPARTMENTS
    )

    # employees (some report to a manager within the same table)
    employees = []
    for i in range(1, 26):
        dept_id = random.randint(1, len(DEPARTMENTS))
        manager_id = random.choice([None] + list(range(1, i))) if i > 1 else None
        employees.append(
            (
                fake.first_name(),
                fake.last_name(),
                fake.unique.email(),
                dept_id,
                fake.date_between(start_date="-5y", end_date="-1y").isoformat(),
                round(random.uniform(45000, 145000), 2),
                manager_id,
            )
        )
    cur.executemany(
        """INSERT INTO employees
           (first_name, last_name, email, department_id, hire_date, salary, manager_id)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        employees,
    )

    # customers
    customers = []
    for _ in range(120):
        customers.append(
            (
                fake.first_name(),
                fake.last_name(),
                fake.unique.email(),
                fake.city(),
                fake.country(),
                fake.date_between(start_date="-3y", end_date="today").isoformat(),
            )
        )
    cur.executemany(
        """INSERT INTO customers (first_name, last_name, email, city, country, signup_date)
           VALUES (?, ?, ?, ?, ?, ?)""",
        customers,
    )

    # products
    products = []
    for _ in range(60):
        products.append(
            (
                fake.word().capitalize() + " " + fake.word().capitalize(),
                random.choice(CATEGORIES),
                round(random.uniform(5, 500), 2),
                random.randint(0, 500),
            )
        )
    cur.executemany(
        """INSERT INTO products (name, category, unit_price, stock_quantity)
           VALUES (?, ?, ?, ?)""",
        products,
    )

    # orders + order_items
    order_row = 1
    for _ in range(400):
        customer_id = random.randint(1, 120)
        employee_id = random.randint(1, 25)
        order_date = fake.date_between(start_date="-2y", end_date="today")
        status = random.choice(STATUSES)
        cur.execute(
            """INSERT INTO orders (customer_id, employee_id, order_date, status)
               VALUES (?, ?, ?, ?)""",
            (customer_id, employee_id, order_date.isoformat(), status),
        )
        order_id = cur.lastrowid
        for _ in range(random.randint(1, 4)):
            product_id = random.randint(1, 60)
            cur.execute("SELECT unit_price FROM products WHERE product_id = ?", (product_id,))
            price = cur.fetchone()[0]
            cur.execute(
                """INSERT INTO order_items (order_id, product_id, quantity, unit_price)
                   VALUES (?, ?, ?, ?)""",
                (order_id, product_id, random.randint(1, 5), price),
            )
        order_row += 1

    conn.commit()
    conn.close()
    print(f"Database built at {DB_PATH}")


if __name__ == "__main__":
    build()
