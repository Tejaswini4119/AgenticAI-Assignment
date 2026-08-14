"""
Builds experiments/04_sql_agent/library.db, a small SQLite database, on
first run. Unlike experiment 1, the agent here is never shown this schema
directly -- it has to discover it through tool calls. Run directly to force
a rebuild.
"""
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "library.db")

AUTHORS = [
    (1, "Ursula K. Le Guin", "USA"),
    (2, "Haruki Murakami", "Japan"),
    (3, "Chimamanda Ngozi Adichie", "Nigeria"),
    (4, "Andy Weir", "USA"),
]

BOOKS = [
    (1, "The Left Hand of Darkness", 1, "Science Fiction", 1969, 2),
    (2, "The Dispossessed", 1, "Science Fiction", 1974, 1),
    (3, "Norwegian Wood", 2, "Fiction", 1987, 3),
    (4, "Kafka on the Shore", 2, "Fiction", 2002, 2),
    (5, "Half of a Yellow Sun", 3, "Historical Fiction", 2006, 2),
    (6, "Americanah", 3, "Fiction", 2013, 1),
    (7, "The Martian", 4, "Science Fiction", 2011, 4),
    (8, "Project Hail Mary", 4, "Science Fiction", 2021, 2),
]

MEMBERS = [
    (1, "Jordan Kim", "2022-01-10", "Denver"),
    (2, "Priya Shah", "2022-06-22", "Denver"),
    (3, "Tomas Novak", "2023-02-05", "Austin"),
    (4, "Aisha Bello", "2023-09-14", "Austin"),
    (5, "Sam O'Connor", "2024-03-01", "Denver"),
]

LOANS = [
    # (id, book_id, member_id, loan_date, return_date)   return_date NULL = still out
    (1, 1, 1, "2024-01-05", "2024-01-19"),
    (2, 7, 2, "2024-02-01", "2024-02-10"),
    (3, 3, 3, "2024-02-15", None),
    (4, 7, 4, "2024-03-01", "2024-03-20"),
    (5, 8, 1, "2024-03-05", None),
    (6, 4, 2, "2024-03-10", "2024-03-25"),
    (7, 7, 5, "2024-04-01", None),
    (8, 5, 3, "2024-04-02", "2024-04-16"),
    (9, 1, 5, "2024-04-20", None),
    (10, 6, 4, "2024-05-01", "2024-05-15"),
]

SCHEMA = """
CREATE TABLE authors (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    country TEXT
);

CREATE TABLE books (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    author_id INTEGER REFERENCES authors(id),
    genre TEXT,
    year INTEGER,
    copies_available INTEGER
);

CREATE TABLE members (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    join_date TEXT,
    city TEXT
);

CREATE TABLE loans (
    id INTEGER PRIMARY KEY,
    book_id INTEGER REFERENCES books(id),
    member_id INTEGER REFERENCES members(id),
    loan_date TEXT,
    return_date TEXT
);
"""


def build(force: bool = False) -> str:
    if force and os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    if os.path.exists(DB_PATH):
        return DB_PATH

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.executescript(SCHEMA)
    cur.executemany("INSERT INTO authors VALUES (?,?,?)", AUTHORS)
    cur.executemany("INSERT INTO books VALUES (?,?,?,?,?,?)", BOOKS)
    cur.executemany("INSERT INTO members VALUES (?,?,?,?)", MEMBERS)
    cur.executemany("INSERT INTO loans VALUES (?,?,?,?,?)", LOANS)
    conn.commit()
    conn.close()
    return DB_PATH


if __name__ == "__main__":
    path = build(force=True)
    print(f"Rebuilt sample database at {path}")
