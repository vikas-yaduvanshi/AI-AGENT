# AI Task Agent — Build Guide (do this today)

A small AI **agent**: give it a goal and it decides which tools to call, runs
them, sees the results, and keeps going until the goal is done. You build it, run
it, and understand it — so it's genuinely yours and you can defend it.

> Honesty first: only put this on your resume once it runs on your laptop and you
> can explain the loop and tool-calling. The "How it works" section maps 1:1 to
> interview questions.

---

## What you are building

```
Goal ─► LLM decides ─► calls a tool ─► tool runs ─► result goes back to LLM
          ▲                                                     │
          └──────────────── loop until done (max 5 steps) ──────┘
                                   │
                              final answer
```

Tools included: a **calculator**, **get_current_time**, and **save_note**
(writes to a file — an example of the agent taking a real action).

---

## Step 1 — Python
Need **Python 3.10+**. Check: `python --version`

## Step 2 — Files
Put `agent.py` and `requirements.txt` in one folder.

## Step 3 — Install
```
python -m venv venv
# Mac/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

pip install -r requirements.txt
```

## Step 4 — Free Groq API key (same as the RAG project)
1. Sign up free at **https://console.groq.com** → **API Keys** → create one.
2. Set it:
```
# Mac/Linux:
export GROQ_API_KEY="paste_your_key_here"
# Windows (Command Prompt):
set GROQ_API_KEY=paste_your_key_here
```

## Step 5 — Run it
```
python agent.py
```
Try goals like:
- `What is 15% of 2400, and save the result as a note.`
- `What is the current time, and save it as a note.`
- `Calculate (120 * 8) - 45.`

Watch the `[step N] calling tool:` lines — that's the agent choosing tools and
acting. Type `exit` to quit. Saved notes appear in `notes.txt`.

---

## How it works (learn these answers)

- **What is an AI agent?** An LLM that plans and uses tools in a loop to achieve a
  goal, instead of just replying once. It can take actions, not only produce text.
- **What is tool / function calling?** I describe my Python functions to the model
  (name, description, inputs). The model can then respond with a request to call
  one, with arguments. My code runs the real function and passes the result back,
  and the model continues. That's the `tools=TOOLS` parameter and the loop in
  `run_agent`.
- **Walk me through the loop.** Send the goal + tool list → if the model asks for a
  tool, run it and append the result as a `tool` message → loop → when the model
  stops asking for tools, that's the final answer.
- **How do you stop it running forever / going wrong?** A `MAX_STEPS` cap so it
  can't loop endlessly; every tool call is wrapped in try/except so an error is
  fed back instead of crashing; and each step is logged for traceability. For
  risky actions you'd add a human-in-the-loop approval and permission checks.
- **How would you extend it?** Add more tools — e.g. a web-search tool or a
  database lookup — by writing the function and adding its description to `TOOLS`.

---

## Step 6 — Push to GitHub
```
git init
echo "venv/" > .gitignore
echo "notes.txt" >> .gitignore
git add .
git commit -m "AI task agent with tool-calling"
```
Create an empty repo on github.com, then:
```
git remote add origin https://github.com/<your-username>/ai-task-agent.git
git branch -M main
git push -u origin main
```
Put the repo link on your resume under the AI Agent project.

---

## Interview talking points
- "I built an AI task agent in Python using tool-calling. It takes a goal, and the
  model decides which tools to call — a calculator, current-time, save-note — in a
  loop until it's done, then gives a final answer."
- Be ready to open `agent.py` and walk through `run_agent`: the message loop, how
  tool calls are executed, and how results are fed back.
- Be honest about scope: "It has a few simple tools and a step cap. To make it
  production-ready I'd add more tools, human approval for risky actions, and
  better observability." Interviewers respect that.

You built this. You can explain it. That's what wins the room.
