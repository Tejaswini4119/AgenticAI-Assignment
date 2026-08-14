"""
Schema catalog for the sample "company" database used by this experiment.

Each table carries a natural-language description of what it holds, on top
of its column list. The description is what gets embedded for retrieval, so
that a question like "who are our top customers" pulls in `customers` and
`orders` without the LLM ever seeing `employees` or `departments`.
"""

TABLES = [
    {
        "name": "customers",
        "description": (
            "Customers who place orders. Includes their name, email, city and "
            "the date they signed up."
        ),
        "columns": [
            ("id", "INTEGER", "primary key"),
            ("name", "TEXT", "full name of the customer"),
            ("email", "TEXT", "contact email"),
            ("city", "TEXT", "city the customer lives in"),
            ("signup_date", "TEXT", "ISO date the customer registered"),
        ],
    },
    {
        "name": "products",
        "description": (
            "Products for sale in the catalog, with category, unit price and "
            "current stock quantity."
        ),
        "columns": [
            ("id", "INTEGER", "primary key"),
            ("name", "TEXT", "product name"),
            ("category", "TEXT", "product category, e.g. Electronics, Books"),
            ("price", "REAL", "unit price in USD"),
            ("stock", "INTEGER", "units currently in stock"),
        ],
    },
    {
        "name": "orders",
        "description": (
            "Orders placed by customers, one row per order, with the order "
            "date and which customer placed it."
        ),
        "columns": [
            ("id", "INTEGER", "primary key"),
            ("customer_id", "INTEGER", "foreign key to customers.id"),
            ("order_date", "TEXT", "ISO date the order was placed"),
            ("status", "TEXT", "one of pending, shipped, delivered, cancelled"),
        ],
    },
    {
        "name": "order_items",
        "description": (
            "Line items belonging to an order: which product, how many units, "
            "and the price at time of purchase. Join to orders and products "
            "to compute revenue or best-sellers."
        ),
        "columns": [
            ("id", "INTEGER", "primary key"),
            ("order_id", "INTEGER", "foreign key to orders.id"),
            ("product_id", "INTEGER", "foreign key to products.id"),
            ("quantity", "INTEGER", "units purchased in this line item"),
            ("unit_price", "REAL", "price per unit at time of purchase"),
        ],
    },
    {
        "name": "employees",
        "description": (
            "Company employees, their job title, salary and which department "
            "they belong to. Unrelated to customer orders."
        ),
        "columns": [
            ("id", "INTEGER", "primary key"),
            ("name", "TEXT", "employee full name"),
            ("title", "TEXT", "job title"),
            ("salary", "REAL", "annual salary in USD"),
            ("department_id", "INTEGER", "foreign key to departments.id"),
        ],
    },
    {
        "name": "departments",
        "description": "Company departments such as Sales, Engineering and Support.",
        "columns": [
            ("id", "INTEGER", "primary key"),
            ("name", "TEXT", "department name"),
        ],
    },
]


def table_names():
    return [t["name"] for t in TABLES]


def get_table(name):
    for t in TABLES:
        if t["name"] == name:
            return t
    raise KeyError(f"Unknown table: {name}")


def to_retrieval_doc(table: dict) -> str:
    """Flatten a table's metadata into one text blob suitable for embedding."""
    col_text = "; ".join(f"{c[0]} ({c[1]}): {c[2]}" for c in table["columns"])
    return f"Table {table['name']}: {table['description']} Columns: {col_text}"


def to_ddl_snippet(table: dict) -> str:
    """Human-readable CREATE TABLE-ish snippet used as LLM context."""
    cols = ", ".join(f"{c[0]} {c[1]}" for c in table["columns"])
    return f"-- {table['description']}\nCREATE TABLE {table['name']} ({cols});"
