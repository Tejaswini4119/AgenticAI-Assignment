import os
import sys

# Ensure parent directory (project root) is in path so we can import utils.llm
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import llm

def main():
    print("=" * 60)
    print("         Task 1: Basic LLM Workflow (Interactive CLI)")
    print("=" * 60)
    print("This script accepts user input and generates a response from the LLM.")
    print("Type 'exit', 'quit', or 'q' to end the session.\n")
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            if not user_input:
                continue
            
            if user_input.lower() in ["exit", "quit", "q"]:
                print("Exiting Task 1. Goodbye!")
                break
                
            print("\nAI is thinking...")
            response = llm.generate_text(user_input)
            print(f"\nAI: {response}")
            
        except KeyboardInterrupt:
            print("\nExiting Task 1. Goodbye!")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()
