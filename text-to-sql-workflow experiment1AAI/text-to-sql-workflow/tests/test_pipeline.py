import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.db import load_schema
from src.executor import UnsafeQueryError, execute_sql, is_read_only
from src.retriever import TfidfRetriever

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "company.db")


def test_load_schema_finds_all_tables():
    tables = load_schema(DB_PATH)
    names = {t.name for t in tables}
    assert names == {"departments", "employees", "customers", "products", "orders", "order_items"}


def test_tfidf_retriever_returns_relevant_tables():
    tables = load_schema(DB_PATH)
    retriever = TfidfRetriever(tables)
    results = retriever.retrieve("Which customers placed the most orders?", top_k=3)
    names = {t.name for t in results}
    assert "customers" in names
    assert "orders" in names


def test_is_read_only_accepts_select():
    assert is_read_only("SELECT * FROM customers;")
    assert is_read_only("WITH x AS (SELECT 1) SELECT * FROM x;")


def test_is_read_only_rejects_mutations():
    assert not is_read_only("DELETE FROM customers;")
    assert not is_read_only("DROP TABLE customers;")
    assert not is_read_only("UPDATE customers SET first_name='x';")


def test_execute_sql_runs_select():
    df = execute_sql("SELECT * FROM departments;", DB_PATH)
    assert len(df) == 5
    assert "name" in df.columns


def test_execute_sql_blocks_mutation():
    try:
        execute_sql("DELETE FROM departments;", DB_PATH)
        assert False, "should have raised"
    except UnsafeQueryError:
        pass
