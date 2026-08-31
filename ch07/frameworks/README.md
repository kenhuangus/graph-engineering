# ch07 framework ports

Classify → research → write → review with a guarded back-edge.

| File | Runtime | Topology note |
|------|---------|----------------|
| `langgraph.py` | LangGraph StateGraph | ('classify', 'research', 'write', 'review') |
| `adk.py` | Google ADK 2.0 | ADK 2.0 Workflow with a review → write back-edge and a halt. Wrappers until you need that edge. |
| `openai_agents.py` | OpenAI Agents SDK | Code orchestration owns the cycle. Handoffs would make the reviewer the new principal; here the reviewer returns a verdict. |
| `anthropic_agents.py` | Claude Agent SDK | query() per node, Python owns the review back-edge budget. Sessions are not a checkpointer. |
| `crewai.py` | CrewAI | Sequential crew can do the happy path. A bounded review cycle is not Process.sequential — move to a graph or a Flow. |

Run any file with `python ch07/frameworks/<name>.py` from the repo root.
Default pytest does not collect these: they are ports, not the grader.
