# Framework ports

Each chapter's homework stays stdlib: the grader in `chNN/tests/` does not import a vendor SDK.

The same chapter predicate is also wrapped in five **live SDK** ports under `chNN/frameworks/`:

| File | Runtime | Live import |
|------|---------|-------------|
| `adk.py` | Google ADK 2.0 `Workflow` function nodes | `from google.adk import Workflow` |
| `openai_agents.py` | OpenAI Agents SDK `Agent` / `Runner` / `handoff` | `from agents import Agent, Runner, handoff` |
| `anthropic_agents.py` | Claude Agent SDK `query` / `ClaudeAgentOptions` | `from claude_agent_sdk import query, ClaudeAgentOptions` |
| `langgraph.py` | LangGraph `StateGraph` | `from langgraph.graph import StateGraph, START, END` |
| `crewai.py` | CrewAI `Crew` / `Task` / `Process` | `from crewai import Agent, Task, Crew, Process` |

`frameworks/runtime.py` is not a stand-in for those constructors. It holds the documented offline extension points (ADK `InMemoryRunner`, an OpenAI `Model` subclass, a CrewAI `BaseLLM`) so the ports execute without a paid key. Node bodies still call the chapter's stdlib module. No network.

Install the five packages, then run a port or the verifier:

```bash
pip install -r requirements-frameworks.txt
python ch04/frameworks/langgraph.py
python ch06/frameworks/adk.py
python frameworks/verify.py
```

`python -m pytest` still grades every chapter's stdlib homework. With the framework extra installed it also runs every port as a script (including under Windows cp1252) plus `frameworks/verify.py`. GitHub Actions on `main` runs both jobs.

## Honesty notes (do not costume)

- **Chapter 5.** Stay on a loop. Do not wrap extract-draft-review as a graph just because five SDKs are present.
- **Chapter 6 / 10.** CrewAI `Process` is `sequential` or `hierarchical` only. Sequential cannot fire a diamond join (`B ∥ C`). That is why Flows exist.
- **Chapter 8 / 12.** `G_K` (triples) and `G_L` (message passing) are not agent graphs.
- **OpenAI.** `manager.as_tool()` keeps the caller as principal. `handoff()` transfers it.
- **Anthropic.** The Agent SDK is Claude Code's tool loop (`claude-agent-sdk`), not the Messages API. Live `query()` talks to Claude CLI; homework `invoke()` constructs real `ClaudeAgentOptions` then runs the chapter tool.
- **ADK 2.0.** Python functions are first-class Workflow nodes. `SequentialAgent` is deprecated; these ports use `Workflow`.
