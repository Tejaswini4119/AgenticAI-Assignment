import os
import sys

# Ensure parent directory (project root) is in path so we can import utils.llm
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from task_3_agentic_ai.agent import SimpleAgent

def main():
    print("=" * 60)
    print("         Task 3: Agentic AI (ReAct Agent)")
    print("=" * 60)
    print("This simple AI agent plans, executes actions using tools, ")
    print("and synthesizes the final output.")
    print("=" * 60)
    
    print("\nPredefined tasks you can run:")
    print("1. Calculate 483 * 29, write the result to 'calc_result.txt', read the file to verify, and return the confirmation.")
    print("2. List all files in the workspace, ask the user for a message, write that message to a file named 'user_note.txt', and verify it by reading it back.")
    print("3. Run a custom task.")
    
    choice = input("\nSelect a task number (1-3): ").strip()
    
    if choice == "1":
        task = "Calculate 483 * 29, write the result to a file named 'calc_result.txt', read the file to verify, and return the confirmation."
    elif choice == "2":
        task = "List all files in the workspace, ask the user for a message, write that message to a file named 'user_note.txt', and verify it by reading it back."
    elif choice == "3":
        task = input("Enter your custom task: ").strip()
        if not task:
            print("No task entered. Exiting.")
            return
    else:
        print("Invalid choice. Running default task 1.")
        task = "Calculate 483 * 29, write the result to a file named 'calc_result.txt', read the file to verify, and return the confirmation."
        
    # Run the agent
    agent = SimpleAgent(max_steps=6)
    result = agent.run(task)
    
    print("\n" + "=" * 60)
    print("AGENT PROCESS COMPLETED")
    print("=" * 60)
    print(f"Result:\n{result}")
    print("=" * 60)

if __name__ == "__main__":
    main()
