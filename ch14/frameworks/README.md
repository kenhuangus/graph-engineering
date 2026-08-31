# ch14 framework ports

retirement_report: dead nodes, dead edges, candidates.

| File | Runtime | Topology note |
|------|---------|----------------|
| `langgraph.py` | LangGraph StateGraph | ('inventory',) |
| `adk.py` | Google ADK 2.0 | A query over declared edges vs traces. Not a Workflow that invents traffic. |
| `openai_agents.py` | OpenAI Agents SDK | One tool: retirement_report. An Agent must not invent unused specialist traffic. |
| `anthropic_agents.py` | Claude Agent SDK | query() may narrate the report. It may not fill dead nodes with guessed walks. |
| `crewai.py` | CrewAI | No crew. Inventory is a graph query. |

Run any file with `python ch14/frameworks/<name>.py` from the repo root.
Default pytest does not collect these: they are ports, not the grader.
