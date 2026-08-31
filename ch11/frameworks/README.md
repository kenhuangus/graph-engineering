# ch11 framework ports

Default-deny invoke, bound resume, cut-vertex reachability.

| File | Runtime | Topology note |
|------|---------|----------------|
| `langgraph.py` | LangGraph StateGraph | ('gate', 'spend') |
| `adk.py` | Google ADK 2.0 | Authz is a node in front of the spend tool, not a prompt. Missing edge is deny. |
| `openai_agents.py` | OpenAI Agents SDK | Guardrail / tool gate. A stranger does not get a handoff to spend. |
| `anthropic_agents.py` | Claude Agent SDK | Permission hook: deny if may_resume is false. Wrong hash is deny. |
| `crewai.py` | CrewAI | Do not put spend on a worker the manager can invent. Pre-assign, or do not crew it. |

Run any file with `python ch11/frameworks/<name>.py` from the repo root.
Default pytest does not collect these: they are ports, not the grader.
