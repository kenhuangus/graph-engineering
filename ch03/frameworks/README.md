# ch03 framework ports

Score a structured system against prompt / context / loop / graph / memory.

| File | Runtime | Topology note |
|------|---------|----------------|
| `langgraph.py` | LangGraph StateGraph | ('score',) |
| `adk.py` | Google ADK 2.0 | One scoring node. Five SequentialAgents would imply a ladder this chapter refuses. |
| `openai_agents.py` | OpenAI Agents SDK | One Agent. Five handoffs, one per sibling, would treat siblings as a promotion path. |
| `anthropic_agents.py` | Claude Agent SDK | query() with a score_layers tool. Primary is argmax, not a vibe. |
| `crewai.py` | CrewAI | One agent, one task. Do not staff five role-agents and vote. |

Run any file with `python ch03/frameworks/<name>.py` from the repo root.
Default pytest does not collect these: they are ports, not the grader.
