"""Generates SQL from a natural-language question + retrieved schema context."""
import re
from typing import List, Optional

from .config import settings
from .db import TableInfo

SYSTEM_PROMPT = """You are an expert data analyst that writes SQLite queries.

Rules:
- Only use the tables and columns given in the provided schema context.
- Return ONLY read-only SELECT statements. Never write INSERT/UPDATE/DELETE/DROP/ALTER.
- Prefer explicit column names over SELECT *.
- Use JOINs (not subqueries) when combining tables, unless a subquery is clearer.
- Wrap the final SQL in a ```sql code block and put nothing else in that block.
- If the question cannot be answered with the given schema, say so in one line
  and do not produce a code block.
"""

FEW_SHOT = """Example
Schema:
Table: customers
Columns:
  - customer_id: INTEGER (PK)
  - first_name: TEXT
  - country: TEXT

Table: orders
Columns:
  - order_id: INTEGER (PK)
  - customer_id: INTEGER (FK->customers.customer_id)
  - order_date: TEXT

Question: How many orders did each country place?
```sql
SELECT c.country, COUNT(o.order_id) AS order_count
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
GROUP BY c.country
ORDER BY order_count DESC;
```
"""


def _build_user_prompt(question: str, tables: List[TableInfo], error_context: Optional[str]) -> str:
    schema_text = "\n\n".join(t.as_document() for t in tables)
    prompt = f"{FEW_SHOT}\n\nSchema:\n{schema_text}\n\nQuestion: {question}\n"
    if error_context:
        prompt += (
            f"\nYour previous SQL failed with this error:\n{error_context}\n"
            "Fix the query and try again, using only the schema above."
        )
    return prompt


def _extract_sql(text: str) -> Optional[str]:
    match = re.search(r"```sql\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip().rstrip(";") + ";"
    return None


class QueryGenerator:
    def __init__(self, api_key: str = None, model: str = None):
        from openai import OpenAI

        self.client = OpenAI(api_key=api_key or settings.openai_api_key)
        self.model = model or settings.generation_model

    def generate(
        self,
        question: str,
        tables: List[TableInfo],
        error_context: Optional[str] = None,
    ) -> Optional[str]:
        """Returns a SQL string, or None if the model declined to answer."""
        user_prompt = _build_user_prompt(question, tables, error_context)
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )
        content = response.choices[0].message.content
        return _extract_sql(content)
