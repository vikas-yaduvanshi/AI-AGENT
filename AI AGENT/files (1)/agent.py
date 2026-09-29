"""
agent.py  —  A minimal AI Task Agent that uses TOOL-CALLING.

WHAT AN AGENT IS:
  A normal chatbot just replies with text. An *agent* is an LLM that can decide
  to call tools (real functions in your code), see the results, and keep going in
  a loop until the goal is done. That's the difference: it can ACT, not just talk.

HOW THIS ONE WORKS:
  1. You give it a goal.
  2. The LLM looks at the goal and the tools it has, and may ask to call a tool.
  3. Our code runs that tool and hands the result back to the LLM.
  4. Repeat until the LLM has enough to give a final answer (or we hit a step cap).

READ EVERY PART. You must be able to explain the loop, tool-calling, and the
safety limits (MAX_STEPS, error handling) in an interview.
"""

import os
import json
import ast
import operator
from datetime import datetime
from openai import OpenAI          # used to call Groq's free, OpenAI-compatible API

# ------------------------------------------------------------------ CONFIG
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
MODEL     = "llama-3.3-70b-versatile"   # if this errors, check console.groq.com/docs/models
MAX_STEPS = 5                           # safety cap so the agent can't loop forever

client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")


# ================================================================== TOOLS
# Each tool is just a normal Python function. The agent can choose to call these.

# -- a tiny SAFE calculator (only arithmetic, no arbitrary code) ------------
_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
        ast.USub: operator.neg}

def _safe_eval(node):
    if isinstance(node, ast.Constant):   # a number
        return node.value
    if isinstance(node, ast.BinOp):      # a + b, a * b, ...
        return _OPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp):    # -a
        return _OPS[type(node.op)](_safe_eval(node.operand))
    raise ValueError("Unsupported expression")

def calculator(expression):
    """Evaluate a basic math expression, e.g. '15/100*2400'."""
    return _safe_eval(ast.parse(expression, mode="eval").body)

def get_current_time():
    """Return the current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def save_note(text):
    """Append a short note to notes.txt (an example of the agent taking an action)."""
    with open("notes.txt", "a", encoding="utf-8") as f:
        f.write(text + "\n")
    return "Saved to notes.txt"

# name -> function, so we can run whatever the LLM asks for
TOOL_FUNCTIONS = {
    "calculator": calculator,
    "get_current_time": get_current_time,
    "save_note": save_note,
}

# The DESCRIPTIONS the LLM sees (so it knows what tools exist and their inputs).
TOOLS = [
    {"type": "function", "function": {
        "name": "calculator",
        "description": "Evaluate a basic arithmetic expression, e.g. '15/100*2400'.",
        "parameters": {"type": "object",
            "properties": {"expression": {"type": "string",
                "description": "The math expression to evaluate."}},
            "required": ["expression"]}}},
    {"type": "function", "function": {
        "name": "get_current_time",
        "description": "Get the current date and time.",
        "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {
        "name": "save_note",
        "description": "Save a short note to a file for later.",
        "parameters": {"type": "object",
            "properties": {"text": {"type": "string",
                "description": "The note text to save."}},
            "required": ["text"]}}},
]


# ================================================================== THE AGENT LOOP
def run_agent(goal):
    messages = [
        {"role": "system", "content":
            "You are a helpful task agent. Use the available tools when they help "
            "you complete the user's goal. Work step by step, call one or more "
            "tools as needed, then give a clear final answer."},
        {"role": "user", "content": goal},
    ]

    for step in range(1, MAX_STEPS + 1):
        response = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOLS,
        )
        msg = response.choices[0].message

        # If the model did NOT ask for a tool, it's giving the final answer.
        if not msg.tool_calls:
            print(f"[step {step}] final answer")
            return msg.content

        # Otherwise, record the assistant's request to call tool(s)...
        messages.append({
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [
                {"id": tc.id, "type": "function",
                 "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                for tc in msg.tool_calls
            ],
        })

        # ...run each requested tool and feed the result back to the model.
        for tc in msg.tool_calls:
            name = tc.function.name
            args = json.loads(tc.function.arguments or "{}")
            print(f"[step {step}] calling tool: {name}({args})")
            try:
                result = TOOL_FUNCTIONS[name](**args)
            except Exception as e:
                result = f"Error: {e}"          # errors go back to the model, don't crash
            print(f"[step {step}]   -> {result}")
            messages.append({
                "role": "tool", "tool_call_id": tc.id, "content": str(result),
            })

    return "Stopped: reached the maximum number of steps."


# ================================================================== RUN
def main():
    if not GROQ_API_KEY:
        print("Please set your GROQ_API_KEY first (see the README).")
        return
    print("AI Task Agent — describe a goal (type 'exit' to quit).")
    print("Try:  What is 15% of 2400, and save the result as a note.\n")
    while True:
        goal = input("Goal: ").strip()
        if goal.lower() in ("exit", "quit"):
            break
        answer = run_agent(goal)
        print(f"\nAgent: {answer}\n")


if __name__ == "__main__":
    main()
