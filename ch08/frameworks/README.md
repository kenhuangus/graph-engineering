# ch08 framework ports

Ingest typed triples, query, walk neighbors, refuse execute().

| File | Runtime | Topology note |
|------|---------|----------------|
| `langgraph.py` | LangGraph StateGraph | ('memory_query',) |
| `adk.py` | Google ADK 2.0 | G_K is a tool, not a Workflow. One memory-query node on G_A. execute() is TypeError. |
| `openai_agents.py` | OpenAI Agents SDK | A store tool on one Agent. Do not hand off to a 'graph agent' that routes. |
| `anthropic_agents.py` | Claude Agent SDK | query() with ingest/query/neighbors tools. No Bash, no routing. |
| `crewai.py` | CrewAI | One researcher-with-a-store is a costume. One tool-bearing agent, or no crew. |

Run any file with `python ch08/frameworks/<name>.py` from the repo root.
Default pytest does not collect these: they are ports, not the grader.
