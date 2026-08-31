# ch04 framework ports

Validate a GraphSpec: typed nodes, edges, S, halt, illegal topologies.

| File | Runtime | Topology note |
|------|---------|----------------|
| `langgraph.py` | LangGraph StateGraph | ('validate',) |
| `adk.py` | Google ADK 2.0 | Workflow node that admits or rejects a spec before any LlmAgent runs. compile() is the ADK analog. |
| `openai_agents.py` | OpenAI Agents SDK | Guardrail before Runner.run. An illegal spec never reaches a handoff. |
| `anthropic_agents.py` | Claude Agent SDK | PreToolUse-style gate: validate_spec before any tool that spends. |
| `crewai.py` | CrewAI | A kickoff that does not call the crew if validate_spec raises. |

Run any file with `python ch04/frameworks/<name>.py` from the repo root.
Default pytest does not collect these: they are ports, not the grader.
