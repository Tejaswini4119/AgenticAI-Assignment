"""SQLite connection and schema introspection utilities."""
import sqlite3
from dataclasses import dataclass, field
from typing import List

from .config import settings


@dataclass
class ColumnInfo:
    name: str
    dtype: str
    is_pk: bool = False
    is_fk: bool = False
    fk_ref: str = ""


@dataclass
class TableInfo:
    name: str
    columns: List[ColumnInfo] = field(default_factory=list)
    sample_rows: List[tuple] = field(default_factory=list)

    def as_document(self) -> str:
        """Flatten table metadata into a text blob used for retrieval + prompting."""
        col_lines = []
        for c in self.columns:
            tag = []
            if c.is_pk:
                tag.append("PK")
            if c.is_fk:
                tag.append(f"FK->{c.fk_ref}")
            tag_str = f" ({', '.join(tag)})" if tag else ""
            col_lines.append(f"  - {c.name}: {c.dtype}{tag_str}")
        header = f"Table: {self.name}\nColumns:\n" + "\n".join(col_lines)
        if self.sample_rows:
            header += "\nSample rows:\n" + "\n".join(str(r) for r in self.sample_rows[:3])
        return header


def get_connection(db_path: str = None) -> sqlite3.Connection:
    return sqlite3.connect(db_path or settings.db_path)


def load_schema(db_path: str = None) -> List[TableInfo]:
    """Introspects every user table in the SQLite DB and returns structured metadata."""
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    table_names = [r[0] for r in cur.fetchall()]

    tables = []
    for tname in table_names:
        cur.execute(f"PRAGMA table_info({tname})")
        pk_cols = set()
        cols_raw = cur.fetchall()
        cur.execute(f"PRAGMA foreign_key_list({tname})")
        fk_rows = cur.fetchall()
        fk_map = {row[3]: f"{row[2]}.{row[4]}" for row in fk_rows}  # from_col -> table.to_col

        columns = []
        for col in cols_raw:
            _, cname, ctype, _, _, pk_flag = col
            if pk_flag:
                pk_cols.add(cname)
            columns.append(
                ColumnInfo(
                    name=cname,
                    dtype=ctype,
                    is_pk=bool(pk_flag),
                    is_fk=cname in fk_map,
                    fk_ref=fk_map.get(cname, ""),
                )
            )

        cur.execute(f"SELECT * FROM {tname} LIMIT 3")
        sample_rows = cur.fetchall()

        tables.append(TableInfo(name=tname, columns=columns, sample_rows=sample_rows))

    conn.close()
    return tables
