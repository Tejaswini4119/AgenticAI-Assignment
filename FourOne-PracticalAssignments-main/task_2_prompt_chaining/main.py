import os
import sys

# Ensure parent directory (project root) is in path so we can import utils.llm
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import llm

def main():
    print("=" * 60)
    print("         Task 2: Prompt Chaining Workflow")
    print("=" * 60)
    print("This script takes a topic, generates a summary, extracts key points,")
    print("and generates three questions using chained LLM prompts.")
    print("=" * 60)
    
    topic = input("\nEnter a topic (e.g. Photosynthesis, Quantum Computing, French Revolution): ").strip()
    if not topic:
        topic = "Artificial Intelligence"
        print(f"No topic entered. Using default: '{topic}'")
        
    print(f"\n[Step 1] Generating summary for topic: '{topic}'...")
    summary_prompt = f"Write a concise summary (around 2 paragraphs) explaining the core concepts of the following topic: {topic}"
    summary = llm.generate_text(summary_prompt)
    
    print("\n" + "-" * 50)
    print("STAGE 1 OUTPUT: SUMMARY")
    print("-" * 50)
    print(summary)
    print("-" * 50)
    
    print(f"\n[Step 2] Extracting key points from the summary...")
    key_points_prompt = f"Based on the following summary, extract the top 5 most important key points. Formulate them as a bulleted list starting with '-':\n\n{summary}"
    key_points = llm.generate_text(key_points_prompt)
    
    print("\n" + "-" * 50)
    print("STAGE 2 OUTPUT: KEY POINTS")
    print("-" * 50)
    print(key_points)
    print("-" * 50)
    
    print(f"\n[Step 3] Generating 3 questions from the key points...")
    questions_prompt = f"Based on the following key points, formulate exactly three thought-provoking questions that test a reader's comprehension of the material:\n\n{key_points}"
    questions = llm.generate_text(questions_prompt)
    
    print("\n" + "-" * 50)
    print("STAGE 3 OUTPUT: COMPREHENSION QUESTIONS")
    print("-" * 50)
    print(questions)
    print("-" * 50)
    
    print("\nPrompt Chaining completed successfully!")

if __name__ == "__main__":
    main()
