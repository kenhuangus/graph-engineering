# ch01 framework ports

Reconstruct a directed naming graph from speech-act events.

| File | Runtime | Topology note |
|------|---------|----------------|
| `langgraph.py` | LangGraph StateGraph | ('ingest', 'emit_edges', 'report') |
| `adk.py` | Google ADK 2.0 | Workflow of ingest → classify_kind → emit_edge. This is G_naming, not a runtime. |
| `openai_agents.py` | OpenAI Agents SDK | One Agent with a tool that builds the graph. No handoff: there is no specialist to own the week. |
| `anthropic_agents.py` | Claude Agent SDK | Claude Agent SDK query() with a single graph-assembly tool. |
| `crewai.py` | CrewAI | Sequential crew: ingest events, then assemble the graph. A hierarchical manager would invent edges. |

Run any file with `python ch01/frameworks/<name>.py` from the repo root.
Default pytest does not collect these: they are ports, not the grader.
