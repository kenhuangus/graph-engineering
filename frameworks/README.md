# Framework ports

Each chapter's homework stays stdlib: the grader in `chNN/tests/` does not import a vendor SDK.

The same chapter predicate is also wrapped in five vendor-shaped ports under `chNN/frameworks/`:

| File | Runtime | Live package |
|------|---------|--------------|
| `adk.py` | Google ADK 2.0 Workflow / LlmAgent | `google-adk` (Workflow GA 19 May 2026) |
| `openai_agents.py` | OpenAI Agents SDK (`Agent`, `Runner`, `handoff`) | `openai-agents` |
| `anthropic_agents.py` | Claude Agent SDK (`query`, `ClaudeAgentOptions`) | `claude-agent-sdk` |
| `langgraph.py` | LangGraph `StateGraph` | `langgraph` |
| `crewai.py` | CrewAI `Crew` / `Task` / `Process` | `crewai` |

Without those packages, `frameworks/runtime.py` supplies constructor-compatible stand-ins. Node bodies still call the chapter's stdlib module. No network. No API key.

## How to run one port

From the repo root:

```bash
python ch04/frameworks/langgraph.py
python ch06/frameworks/adk.py
python ch07/frameworks/openai_agents.py
```

## How to verify all 70 ports

```bash
python frameworks/verify.py
```

Default `python -m pytest` does not collect `frameworks/` (`norecursedirs`). Optional live SDKs:

```bash
pip install -r requirements-frameworks.txt
```

Swap the `from runtime import …` line in a port for the live import named in that file's docstring.

## Honesty notes (do not costume)

- **Chapter 5.** Stay on a loop. Do not wrap extract-draft-review as a graph just because five SDKs are present.
- **Chapter 6 / 10.** CrewAI `Process` is `sequential` or `hierarchical` only. Sequential cannot fire a diamond join (`B ∥ C`). That is why Flows exist.
- **Chapter 8 / 12.** `G_K` (triples) and `G_L` (message passing) are not agent graphs.
- **OpenAI.** `manager.as_tool()` keeps the caller as principal. `handoff()` transfers it.
- **Anthropic.** The Agent SDK is Claude Code's tool loop (`claude-agent-sdk`), not the Messages API.
- **ADK 2.0.** Use `LlmAgent` / `SequentialAgent` / `ParallelAgent` until a back-edge earns a `Workflow`.
