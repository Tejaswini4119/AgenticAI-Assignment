"""
Streamlit demo for the Text-to-SQL workflow.

Run:
    streamlit run app_streamlit.py
"""
import streamlit as st

from src.pipeline import TextToSQLPipeline

st.set_page_config(page_title="Text-to-SQL Workflow", page_icon="🗄️", layout="wide")
st.title("🗄️ Text-to-SQL Workflow")
st.caption("Retrieval-augmented natural language → SQL, over a sample SQLite database.")


@st.cache_resource
def get_pipeline():
    return TextToSQLPipeline()


question = st.text_input(
    "Ask a question about the data",
    placeholder="e.g. What are the top 5 best-selling products by revenue?",
)

if st.button("Run", type="primary") and question:
    with st.spinner("Retrieving schema and generating SQL..."):
        try:
            pipeline = get_pipeline()
            result = pipeline.ask(question)
        except Exception as e:
            st.error(f"Pipeline error: {e}")
            st.stop()

    st.subheader("1. Retrieved tables")
    st.write(", ".join(result.retrieved_tables))

    if result.sql:
        st.subheader("2. Generated SQL")
        st.code(result.sql, language="sql")

    st.subheader("3. Result")
    if result.success:
        st.dataframe(result.result, use_container_width=True)
    else:
        st.error(result.error)

    if result.attempts > 1:
        st.info(f"Query was self-repaired after a failed attempt ({result.attempts} attempts total).")
