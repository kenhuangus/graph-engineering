# ch09 framework ports

Step runner: retry + jitter, idempotency, circuit breaker.

| File | Runtime | Topology note |
|------|---------|----------------|
| `langgraph.py` | LangGraph StateGraph | ('step',) |
| `adk.py` | Google ADK 2.0 | RetryConfig on the node. A Workflow does not replace idempotency keys. |
| `openai_agents.py` | OpenAI Agents SDK | Runner retries are not idempotency. Wrap the side effect in StepRunner. |
| `anthropic_agents.py` | Claude Agent SDK | Hooks can deny a replay. The key still lives in your runner. |
| `crewai.py` | CrewAI | kickoff() twice is not at-least-once. Put StepRunner under the task body. |

Run any file with `python ch09/frameworks/<name>.py` from the repo root.
Default pytest does not collect these: they are ports, not the grader.
