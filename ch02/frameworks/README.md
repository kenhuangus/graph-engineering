# ch02 framework ports

Classify a GraphObject as G_A, G_K, or a run trace; refuse mash-ups.

| File | Runtime | Topology note |
|------|---------|----------------|
| `langgraph.py` | LangGraph StateGraph | ('inspect', 'classify', 'halt') |
| `adk.py` | Google ADK 2.0 | Single-turn LlmAgent is the wrong altitude. A Workflow node calls classify() and halt. |
| `openai_agents.py` | OpenAI Agents SDK | One Agent, no handoff. Mash-up refusal is a guardrail, not a specialist. |
| `anthropic_agents.py` | Claude Agent SDK | query() plus a classify tool. The model does not get to rename the rooms. |
| `crewai.py` | CrewAI | One agent, one task. A crew of three 'G_A / G_K / trace' voters is a costume. |

Run any file with `python ch02/frameworks/<name>.py` from the repo root.
Default pytest does not collect these: they are ports, not the grader.
