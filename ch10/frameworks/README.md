# ch10 framework ports

Kahn topological sort, cycle detection, ready-set on a diamond.

| File | Runtime | Topology note |
|------|---------|----------------|
| `langgraph.py` | LangGraph StateGraph | ('A', 'B', 'C', 'D') |
| `adk.py` | Google ADK 2.0 | A diamond is Sequential + Parallel wrappers, or a Workflow with a join. A back-edge is not a DAG. |
| `openai_agents.py` | OpenAI Agents SDK | Code orchestration: asyncio-shaped B||C after A, then D. Handoffs cannot express a join. |
| `anthropic_agents.py` | Claude Agent SDK | query() is not Kahn. Python runs topological_sort; the SDK does not. |
| `crewai.py` | CrewAI | Process.sequential cannot fire B and C together. Admit the join or do not draw a diamond. |

Run any file with `python ch10/frameworks/<name>.py` from the repo root.
Default pytest does not collect these: they are ports, not the grader.
