# ch05 framework ports

Napkin test: stay on a loop or earn a graph. Sequential status copy stays a loop.

| File | Runtime | Topology note |
|------|---------|----------------|
| `langgraph.py` | LangGraph StateGraph | ('napkin',) |
| `adk.py` | Google ADK 2.0 | LlmAgent / LoopAgent wrapper if the napkin says loop. Do not reach for Workflow of extract-draft-review. |
| `openai_agents.py` | OpenAI Agents SDK | One Agent, no handoffs. A manager with three specialist tools is the 3-node costume. |
| `anthropic_agents.py` | Claude Agent SDK | One query() loop. Three sequential queries is the bakeoff graph that did not earn its keep. |
| `crewai.py` | CrewAI | Do not staff a three-agent sequential crew for one paragraph. One agent, one task, or no crew. |

Run any file with `python ch05/frameworks/<name>.py` from the repo root.
Default pytest does not collect these: they are ports, not the grader.
