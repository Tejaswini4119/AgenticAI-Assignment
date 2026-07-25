import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from .tools import ALL_TOOLS
from utils import llm

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
load_dotenv(dotenv_path)
api_key = os.getenv("GEMINI_API_KEY")

class SimpleAgent:
    def __init__(self, max_steps: int = 6):
        self.max_steps = max_steps
        self.history = []
        
        # Initialize Google GenAI Chat Model using LangChain
        # We explicitly pass the loaded api_key to be robust and target gemini-flash-latest
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-flash-latest",
            temperature=0,
            google_api_key=api_key
        )
        
        # Create the agent executor using LangGraph ReAct agent
        # It automatically coordinates model execution, tool binding, and scratchpad history!
        self.agent_executor = create_react_agent(
            model=self.llm,
            tools=ALL_TOOLS
        )

    def run(self, task: str) -> str:
        # Check if the global LLM utility is already in mock mode (e.g. key exhausted)
        if llm.USE_MOCK:
            print("\n[Agent Warning] API is rate-limited/exhausted. Bypassing LangGraph to run custom Python ReAct fallback.")
            return self.run_python_fallback(task)
            
        print(f"\n[Agent] Starting task using LangGraph ReAct framework: '{task}'")
        try:
            # Attempt live execution via LangGraph
            result = self.agent_executor.invoke({
                "messages": [("human", task)]
            })
            
            # LangGraph returns all messages in the state graph. The last message contains the final answer.
            final_message = result["messages"][-1]
            content = final_message.content
            
            # Format and clean response content if it's returned as a list of dicts
            if isinstance(content, list):
                text_parts = []
                for part in content:
                    if isinstance(part, dict) and "text" in part:
                        text_parts.append(part["text"])
                    elif isinstance(part, str):
                        text_parts.append(part)
                return "\n".join(text_parts)
            return str(content)
            
        except Exception as e:
            # Catch rate limit / model errors and fall back to custom ReAct loop
            print(f"\n[Agent Warning] Live LangGraph call failed (e.g. rate limit): {e}")
            llm.USE_MOCK = True  # Switch LLM utility to mock mode
            return self.run_python_fallback(task)

    def run_python_fallback(self, task: str) -> str:
        print("[Agent] Falling back to custom Python ReAct execution loop...")
        from .tools import TOOL_MAP
        
        self.history = [{"role": "user", "content": task}]
        
        for step in range(1, self.max_steps + 1):
            print(f"\n--- [Agent Step {step}] ---")
            prompt = self._build_prompt()
            
            try:
                # This will return structured JSON responses (mock if USE_MOCK is True)
                response_json = llm.generate_json(prompt)
            except Exception as e:
                print(f"[Agent Error] Failed to generate JSON: {e}")
                return f"Task failed due to LLM error: {e}"
                
            thought = response_json.get("thought", "Thinking...")
            print(f"Thought: {thought}")
            
            # Check for final answer
            if "final_answer" in response_json:
                print(f"\n[Agent] Final Answer: {response_json['final_answer']}")
                self.history.append({"role": "assistant", "content": json.dumps(response_json)})
                return response_json["final_answer"]
                
            # Check for tool call
            if "call_tool" in response_json:
                tool_call = response_json["call_tool"]
                tool_name = tool_call.get("name")
                tool_args = tool_call.get("args", {})
                
                print(f"Action: Call tool '{tool_name}' with args {tool_args}")
                
                if tool_name in TOOL_MAP:
                    try:
                        # Invoke LangChain tool function
                        observation = TOOL_MAP[tool_name].invoke(tool_args)
                    except Exception as e:
                        observation = f"Error executing tool '{tool_name}': {e}"
                else:
                    observation = f"Error: Tool '{tool_name}' is not supported."
                    
                print(f"Observation: {observation}")
                
                # Append tool call and observation to history
                self.history.append({"role": "assistant", "content": json.dumps(response_json)})
                self.history.append({"role": "system", "content": f"Observation from '{tool_name}': {observation}"})
            else:
                print("[Agent Error] LLM returned invalid JSON protocol.")
                return "Task aborted due to invalid model response protocol."
                
        print("\n[Agent] Max steps reached without final answer.")
        return "Task could not be completed within the step limit."

    def _build_prompt(self) -> str:
        prompt_parts = ["Here is the history of the conversation and actions taken so far:"]
        for entry in self.history:
            role = entry["role"]
            content = entry["content"]
            if role == "user":
                prompt_parts.append(f"User Task: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Agent Action: {content}")
            elif role == "system":
                prompt_parts.append(f"System Observation: {content}")
        
        prompt_parts.append("\nWhat is your next step? Answer in JSON format.")
        return "\n".join(prompt_parts)
