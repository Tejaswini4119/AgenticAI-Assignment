"""
End-to-end Text-to-SQL pipeline.

Flow for each question:
  1. RETRIEVE  -> select the top-k most relevant tables for the question
  2. GENERATE  -> ask the LLM for a SQL query grounded in those tables
  3. EXECUTE   -> run the query against SQLite
  4. REPAIR    -> if execution fails, feed the error back to the LLM and
                  retry (bounded by max_repair_attempts) - a small agentic
                  feedback loop rather than a single blind LLM call.
"""
from dataclasses import dataclass, field
from typing import List, Optional

import pandas as pd

from .config import settings
from .executor import UnsafeQueryError, execute_sql
from .generator import QueryGenerator
from .retriever import BaseRetriever, build_retriever


@dataclass
class PipelineResult:
    question: str
    retrieved_tables: List[str]
    sql: Optional[str] = None
    result: Optional[pd.DataFrame] = None
    error: Optional[str] = None
    attempts: int = 0
    history: List[str] = field(default_factory=list)  # sql attempted at each step

    @property
    def success(self) -> bool:
        return self.error is None and self.sql is not None


class TextToSQLPipeline:
    def __init__(self, db_path: str = None, retriever: BaseRetriever = None, generator: QueryGenerator = None):
        self.db_path = db_path or settings.db_path
        self.retriever = retriever or build_retriever(self.db_path)
        self.generator = generator or QueryGenerator()

    def ask(self, question: str, top_k: int = None) -> PipelineResult:
        top_k = top_k or settings.top_k_tables
        tables = self.retriever.retrieve(question, top_k)
        result = PipelineResult(question=question, retrieved_tables=[t.name for t in tables])

        error_context = None
        for attempt in range(1, settings.max_repair_attempts + 2):  # 1 initial + N repairs
            result.attempts = attempt
            sql = self.generator.generate(question, tables, error_context=error_context)

            if sql is None:
                result.error = "Model declined to generate SQL for this question."
                return result

            result.sql = sql
            result.history.append(sql)

            try:
                result.result = execute_sql(sql, self.db_path)
                result.error = None
                return result
            except UnsafeQueryError as e:
                result.error = str(e)
                return result  # don't retry unsafe queries
            except Exception as e:  # sqlite3.Error and friends
                error_context = str(e)
                result.error = error_context
                continue

        return result
