# ch13 framework ports

check_trace: halt, join, unconstrained spend.

| File | Runtime | Topology note |
|------|---------|----------------|
| `langgraph.py` | LangGraph StateGraph | ('check',) |
| `adk.py` | Google ADK 2.0 | Eval is a node after the run, or a CI job. It does not call a model. |
| `openai_agents.py` | OpenAI Agents SDK | Do not ask an Agent whether the join completed. check_trace reads the walk. |
| `anthropic_agents.py` | Claude Agent SDK | No query(). The checker is code. |
| `crewai.py` | CrewAI | A reviewer agent is not an invariant. The grader is check_trace. |

Run any file with `python ch13/frameworks/<name>.py` from the repo root.
Default pytest does not collect these: they are ports, not the grader.
