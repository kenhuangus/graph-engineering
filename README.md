# Graph Engineering — Companion Homework

Companion homework for **Graph Engineering** by Ken Huang.

Canonical repo: https://github.com/kenhuangus/graph-engineering (public; owner `kenhuangus`).

These are **reference solutions**. Attempt the assignment in each chapter's `homework.md` before reading `src/`. The tests are the grader: they assert observable behavior, not imports.

## How to run

From this directory (the homework root):

```bash
pip install -r requirements.txt
python -m pytest
```

Or from anywhere:

```bash
python -m pytest
```

That command collects **every chapter**. You can also run one chapter:

```bash
python -m pytest ch06 -v
```

Constraints for every chapter: Python 3.12+, pytest, stdlib only (numpy is not required). Tests do not use the network and do not call paid APIs.

## Framework ports

Each chapter also ships five implementations under `chNN/frameworks/` that import the live vendor SDKs: Google ADK 2.0 (`google.adk.Workflow`), OpenAI Agents SDK (`agents.Agent` / `Runner`), Anthropic Claude Agent SDK (`claude_agent_sdk.query` / `ClaudeAgentOptions`), LangGraph (`langgraph.graph.StateGraph`), and CrewAI (`crewai.Crew` / `Process`). Node bodies still call the chapter stdlib module. Default homework tests stay stdlib-only. To execute the ports:

```bash
pip install -r requirements-frameworks.txt
python ch04/frameworks/langgraph.py
python frameworks/verify.py
```

See `frameworks/README.md`. No paid API keys: ADK function nodes, a local OpenAI `Model` subclass, CrewAI `BaseLLM`, and LangGraph `compile().invoke()` all run offline. Claude `query()` needs Claude CLI; the port type-checks live `ClaudeAgentOptions` then runs the chapter tool.

## Chapter index

| Dir  | Chapter | One-line assignment |
|------|---------|---------------------|
| ch01 | The Week the Word Arrived | Reconstruct a directed naming graph from speech-act events and detect a claimed coincidence edge. |
| ch02 | Two Graphs, One Word | Classify a `GraphObject` as `G_A`, `G_K`, or a run trace; reject mash-ups with a reason code. |
| ch03 | Harness as Paradigm — Siblings, Not a Ladder | Score a structured system description against prompt / context / loop / graph / memory. |
| ch04 | Anatomy of an Agent Graph | Validate a `GraphSpec` (typed nodes, edges, state `S`, halt, optional interrupt). |
| ch05 | When Not to Build a Graph | Napkin test: `JobSpec` → stay on a loop or build a graph, with closed-set reasons. |
| ch06 | Patterns That Earn Their Keep | Tiny runtime: `sequential_path`, `supervisor_star`, `fanout_join` on the same job. |
| ch07 | Frameworks You Can Ship On | Mini `StateGraph`: nodes, edges, reducers, `compile()`, `invoke()`, guarded cycle. |
| ch08 | Knowledge Graphs as Memory | `TripleStore`: ingest with provenance, wildcard query, neighbor walk; refuse `execute()`. |
| ch09 | Operating Graphs in Production | Step runner: bounded retry + jitter, idempotency keys, circuit breaker. |
| ch10 | Computer Science (Kahn / DAG) | `topological_sort`, `has_cycle`, `ready_set` on a diamond DAG. |
| ch11 | Security, Identity, Governance | Authz graph: default-deny invoke, bound resume, cut-vertex reachability. |
| ch12 | Graph Intelligence | One-layer message passing: `normalize(self + sum(neighbors))`. |
| ch13 | Testing, Evaluation, Verification | `check_trace(trace, spec)` for halt, join, and unconstrained spend. |
| ch14 | After the Word Dies | `retirement_report(spec, traces)`: dead nodes, dead edges, candidates. |

## Book listings vs homework modules

In-chapter listings are pedagogical programs. The graded homework is the smaller public API in `chNN/src/`. Chapter 10 and 11 ship both files: run `python ch10/src/chapter10_three_machines.py` and `python ch11/src/chapter11_authz_reachability.py` from the repo root.

| Dir  | In-chapter listing (if named) | Graded module |
|------|-------------------------------|---------------|
| ch03 | five sibling layers | `five_layers.py` |
| ch05 | `loop_vs_graph_bakeoff.py` | `napkin.py` |
| ch06 | `ch06_workers_messages.py` | `pattern_runtime.py` |
| ch08 | `memory_graph_node.py` | `triple_store.py` |
| ch10 | `chapter10_three_machines.py` | `kahn.py` |
| ch11 | `chapter11_authz_reachability.py` | `authz_graph.py` |

Homework URLs in the manuscript point at `https://github.com/kenhuangus/graph-engineering/tree/main/chNN/`.

## Layout of a chapter

```
chNN/
  homework.md   # the assignment (do this first)
  src/          # complete reference implementation
  tests/        # pytest that grades the public API
  frameworks/   # ADK / OpenAI / Claude Agent SDK / LangGraph / CrewAI ports
```

Tests import the public module names from `src/` via `pytest.ini` `pythonpath`. To grade your own module, put it on `PYTHONPATH` *ahead* of `src/` or replace the file in `src/`. Tests fail when the logic is wrong.

## License

MIT License. Copyright (c) 2026 Ken Huang.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
