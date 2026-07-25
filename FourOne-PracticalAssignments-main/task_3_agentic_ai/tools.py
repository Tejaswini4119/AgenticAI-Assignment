import os
import datetime
from langchain_core.tools import tool

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@tool
def calculate(expression: str) -> str:
    """Evaluates a mathematical expression safely. Input 'expression' is a string, e.g. '123 * 45'."""
    allowed_chars = set("0123456789+-*/(). ")
    cleaned = "".join(c for c in expression if c in allowed_chars)
    try:
        result = eval(cleaned, {"__builtins__": None}, {})
        return str(result)
    except Exception as e:
        return f"Error evaluating expression: {e}"

@tool
def write_file(filename: str, content: str) -> str:
    """Writes text content to a file in the workspace. Input arguments are 'filename' (string) and 'content' (string)."""
    safe_filename = os.path.basename(filename)
    filepath = os.path.join(WORKSPACE_DIR, safe_filename)
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to {safe_filename}."
    except Exception as e:
        return f"Error writing file: {e}"

@tool
def read_file(filename: str) -> str:
    """Reads text content from a file in the workspace. Input argument is 'filename' (string)."""
    safe_filename = os.path.basename(filename)
    filepath = os.path.join(WORKSPACE_DIR, safe_filename)
    if not os.path.exists(filepath):
        return f"Error: File '{safe_filename}' does not exist."
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

@tool
def get_current_time() -> str:
    """Returns the current system date and time. No input arguments."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@tool
def list_directory() -> str:
    """Lists all files in the current workspace directory. No input arguments."""
    try:
        files = [f for f in os.listdir(WORKSPACE_DIR) if os.path.isfile(os.path.join(WORKSPACE_DIR, f))]
        return f"Files in workspace: {', '.join(files) if files else 'None'}"
    except Exception as e:
        return f"Error listing directory: {e}"

@tool
def delete_file(filename: str) -> str:
    """Deletes a file from the workspace. Input argument is 'filename' (string)."""
    safe_filename = os.path.basename(filename)
    filepath = os.path.join(WORKSPACE_DIR, safe_filename)
    if not os.path.exists(filepath):
        return f"Error: File '{safe_filename}' does not exist."
    try:
        os.remove(filepath)
        return f"Successfully deleted {safe_filename}."
    except Exception as e:
        return f"Error deleting file: {e}"

@tool
def ask_user_clarification(question: str) -> str:
    """Asks the user a question to clarify ambiguous instructions or request further details. Input argument is 'question' (string)."""
    print(f"\n[AGENT QUESTION]: {question}")
    user_response = input("Your response: ").strip()
    return f"User response: {user_response}"

ALL_TOOLS = [
    calculate,
    write_file,
    read_file,
    get_current_time,
    list_directory,
    delete_file,
    ask_user_clarification
]

TOOL_MAP = {
    "calculate": calculate,
    "write_file": write_file,
    "read_file": read_file,
    "get_current_time": get_current_time,
    "list_directory": list_directory,
    "delete_file": delete_file,
    "ask_user_clarification": ask_user_clarification
}
