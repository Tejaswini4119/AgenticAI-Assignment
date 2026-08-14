import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent import SQLReActAgent


def print_step(step, thought, error=None, final_answer=None, tool=None, args=None, observation=None):
    print(f"\n--- Step {step} ---")
    if error:
        print(f"Error: {error}")
        return
    print(f"Thought: {thought}")
    if final_answer is not None:
        print(f"Final Answer: {final_answer}")
        return
    print(f"Action: {tool}({args})")
    print(f"Observation: {observation}")


def main():
    print("=" * 70)
    print("  Experiment 4: SQL Agent with Tool Use (ReAct)")
    print("=" * 70)
    print("The agent knows NOTHING about the database schema up front -- it")
    print("has to call list_tables/get_schema itself before querying.")
    print("Type 'exit'/'quit' to leave.\n")
    print("Try: 'which books are currently on loan and not yet returned?'")
    print("     'who are the most active borrowers?'")
    print("     'how many books has each author written?'\n")

    while True:
        try:
            question = input("Question: ").strip()
            if not question:
                continue
            if question.lower() in ("exit", "quit", "q"):
                print("Goodbye!")
                break

            agent = SQLReActAgent(max_steps=8, on_step=print_step)
            answer = agent.run(question)
            print(f"\n[result] {answer}\n")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
