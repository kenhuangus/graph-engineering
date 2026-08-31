# ch06 framework ports

Same job on sequential_path, supervisor_star, and fanout_join.

| File | Runtime | Topology note |
|------|---------|----------------|
| `langgraph.py` | LangGraph StateGraph | ('classify', 'research_web', 'research_docs', 'write') |
| `adk.py` | Google ADK 2.0 | SequentialAgent for the path; ParallelAgent + join for fan-out; a coordinator LlmAgent for the star. |
| `openai_agents.py` | OpenAI Agents SDK | Code-orchestrated sequential; manager.as_tool() for the star; asyncio-shaped fan-out for the join. |
| `anthropic_agents.py` | Claude Agent SDK | Three query() tools in a line, a hub tool for the star, parallel tools then synthesize for the join. |
| `crewai.py` | CrewAI | Process.sequential is the path. Process.hierarchical is the star. There is no join process — that is why Flows exist. |

Run any file with `python ch06/frameworks/<name>.py` from the repo root.
Default pytest does not collect these: they are ports, not the grader.
