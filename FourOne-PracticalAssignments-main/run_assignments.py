import os
import sys
import subprocess
from utils.tui import interactive_select

def run_task(script_path):
    # Runs the task in a subprocess using the virtual environment's python interpreter
    venv_python = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv", "bin", "python")
    if not os.path.exists(venv_python):
        venv_python = sys.executable  # Fallback to current python interpreter if venv doesn't exist
        
    try:
        subprocess.run([venv_python, script_path], check=True)
    except KeyboardInterrupt:
        print("\nTask interrupted by user.")
    except Exception as e:
        print(f"\nError running task: {e}")

def run_verification():
    print("\n" + "=" * 60)
    print("         SYSTEM VERIFICATION & SELF-TESTS")
    print("=" * 60)
    
    # Test 1: Check environment & API keys
    print("Test 1: Environment Check...")
    from utils import llm
    api_key_set = os.getenv("GEMINI_API_KEY") is not None
    print(f"  - GEMINI_API_KEY found: {api_key_set}")
    print(f"  - Currently running in: {'Offline Mode (No API key)' if llm.USE_MOCK else 'LIVE API Mode'}")
    
    # Test 2: Cosine Similarity math check
    print("\nTest 2: Cosine Similarity check...")
    v1 = [1.0, 2.0, 3.0]
    v2 = [1.0, 2.0, 3.0]
    v3 = [-1.0, -2.0, -3.0]
    sim_identical = llm.cosine_similarity(v1, v2)
    sim_opposite = llm.cosine_similarity(v1, v3)
    print(f"  - Similarity of identical vectors: {sim_identical:.4f} (Expected: 1.0000)")
    print(f"  - Similarity of opposite vectors: {sim_opposite:.4f} (Expected: -1.0000)")
    assert abs(sim_identical - 1.0) < 1e-6, "Similarity of identical vectors failed"
    assert abs(sim_opposite - (-1.0)) < 1e-6, "Similarity of opposite vectors failed"
    print("  -> Cosine similarity calculation is CORRECT.")
    
    # Test 3: LLM generation test
    print("\nTest 3: Basic LLM generation response test...")
    try:
        response = llm.generate_text("Say 'Verification Success'")
        print(f"  - Query: 'Say Verification Success'")
        print(f"  - LLM Output: {response.strip()}")
        print("  -> LLM connection check PASSED.")
    except Exception as e:
        print(f"  -> LLM connection check FAILED: {e}")
        
    # Test 4: JSON generation test
    print("\nTest 4: Structured JSON generation test...")
    try:
        json_output = llm.generate_json("Return a JSON containing a single field 'status' with value 'active'")
        print(f"  - LLM Output: {json_output}")
        print("  -> Structured JSON check PASSED.")
    except Exception as e:
        print(f"  -> Structured JSON check FAILED: {e}")

    print("\n" + "=" * 60)
    print("Verification completed!")
    print("=" * 60)

def main():
    options = [
        "Task 1: Basic LLM Workflow (Interactive CLI)",
        "Task 2: Prompt Chaining Workflow",
        "Task 3: Agentic AI (ReAct Agent)",
        "Task 4: RAG-Based Question Answering",
        "Run System Verification / Self-Tests",
        "Exit"
    ]
    
    while True:
        # Try TUI selection first
        choice_idx = interactive_select(options, title="Agentic AI Assignment 1 - Launcher Menu:")
        
        # If TUI fails (e.g. non-TTY), fall back to standard printing
        if choice_idx == -1:
            print("\n" + "=" * 60)
            print("     Agentic AI Assignment 1 - Practical Submissions")
            print("=" * 60)
            for idx, opt in enumerate(options):
                print(f"{idx + 1}. {opt}")
            print("=" * 60)
            
            choice_str = input(f"Enter your choice (1-{len(options)}): ").strip()
            if choice_str.isdigit() and 1 <= int(choice_str) <= len(options):
                choice_idx = int(choice_str) - 1
            else:
                print(f"Invalid choice. Please select 1-{len(options)}.")
                continue

        # Handle option selected
        if choice_idx == 0:
            run_task("task_1_llm_workflow/main.py")
        elif choice_idx == 1:
            run_task("task_2_prompt_chaining/main.py")
        elif choice_idx == 2:
            run_task("task_3_agentic_ai/main.py")
        elif choice_idx == 3:
            run_task("task_4_rag_qa/main.py")
        elif choice_idx == 4:
            run_verification()
        elif choice_idx == 5:
            print("Exiting launcher. Goodbye!")
            break

if __name__ == "__main__":
    main()
