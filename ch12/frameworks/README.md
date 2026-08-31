# ch12 framework ports

One-layer message passing. This is G_L, not an agent graph.

| File | Runtime | Topology note |
|------|---------|----------------|
| `langgraph.py` | LangGraph StateGraph | ('message_pass',) |
| `adk.py` | Google ADK 2.0 | A single function node. Do not ParallelAgent the neighbors as workers. |
| `openai_agents.py` | OpenAI Agents SDK | No agents. If you wrap this in Runner, you have costumed linear algebra. |
| `anthropic_agents.py` | Claude Agent SDK | query() is optional narration. The update rule is normalize(self + sum(neighbors)). |
| `crewai.py` | CrewAI | A crew of nodes is the category error this chapter exists to prevent. |

Run any file with `python ch12/frameworks/<name>.py` from the repo root.
Default pytest does not collect these: they are ports, not the grader.
