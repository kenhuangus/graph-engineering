"""Two graphs, one doorway. SQLite is G_K. The function list is G_A.

Save as memory_graph_node.py and run: python memory_graph_node.py
"""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from datetime import date

ALLOWED_NODE_TYPES = ("Person", "Design", "ADR", "Incident", "Document")

SHAPES = {
    ("Design", "supersedes", "Design"),
    ("ADR", "decided_by", "Person"),
    ("ADR", "caused_by", "Incident"),
    ("Design", "decided_in", "ADR"),
    ("Document", "mentions", "Incident"),
    ("Document", "mentions", "Design"),
    ("Document", "mentions", "Person"),
    ("Document", "mentions", "ADR"),
}

SCHEMA_SQL = (
    "CREATE TABLE IF NOT EXISTS nodes ("
    " id TEXT PRIMARY KEY, ntype TEXT NOT NULL, name TEXT NOT NULL,"
    " props TEXT NOT NULL DEFAULT '{}');"
    "CREATE TABLE IF NOT EXISTS edges ("
    " id INTEGER PRIMARY KEY AUTOINCREMENT,"
    " src TEXT NOT NULL, predicate TEXT NOT NULL, dst TEXT NOT NULL,"
    " valid_from TEXT NOT NULL, valid_to TEXT,"
    " learned_at TEXT NOT NULL, source TEXT NOT NULL);"
)


class ShapeError(ValueError):
    pass


class MemoryGraph:
    def __init__(self, path="memory_graph.sqlite"):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA_SQL)
        self.conn.commit()

    def upsert_node(self, node_id, ntype, name, **props):
        if ntype not in ALLOWED_NODE_TYPES:
            raise ShapeError("unknown node type: " + ntype)
        self.conn.execute(
            "INSERT INTO nodes(id, ntype, name, props) VALUES (?,?,?,?) "
            "ON CONFLICT(id) DO UPDATE SET ntype=excluded.ntype, "
            "name=excluded.name, props=excluded.props",
            (node_id, ntype, name, json.dumps(props)),
        )
        self.conn.commit()

    def write_edge(
        self,
        src,
        predicate,
        dst,
        valid_from,
        learned_at,
        source,
        valid_to=None,
        invalidate_previous=True,
    ):
        st = self.conn.execute("SELECT ntype FROM nodes WHERE id=?", (src,)).fetchone()
        dt = self.conn.execute("SELECT ntype FROM nodes WHERE id=?", (dst,)).fetchone()
        if st is None or dt is None:
            raise ShapeError("unresolved endpoint: %s -> %s" % (src, dst))
        if (st["ntype"], predicate, dt["ntype"]) not in SHAPES:
            raise ShapeError(
                "SHACL fail: %s-[%s]->%s not in shapes" % (st["ntype"], predicate, dt["ntype"])
            )
        if invalidate_previous:
            self.conn.execute(
                "UPDATE edges SET valid_to=? WHERE src=? AND predicate=? "
                "AND valid_to IS NULL AND dst!=?",
                (valid_from, src, predicate, dst),
            )
        self.conn.execute(
            "INSERT INTO edges(src, predicate, dst, valid_from, valid_to, "
            "learned_at, source) VALUES (?,?,?,?,?,?,?)",
            (src, predicate, dst, valid_from, valid_to, learned_at, source),
        )
        self.conn.commit()

    def neighborhood(self, seed, hops, day):
        seen = {seed}
        frontier = {seed}
        facts = {}
        for _ in range(hops):
            nxt = set()
            for node in frontier:
                rows = self.conn.execute(
                    "SELECT e.*, s.name AS src_name, d.name AS dst_name "
                    "FROM edges e JOIN nodes s ON s.id=e.src "
                    "JOIN nodes d ON d.id=e.dst "
                    "WHERE (e.src=? OR e.dst=?) AND e.valid_from<=? "
                    "AND (e.valid_to IS NULL OR e.valid_to>?)",
                    (node, node, day, day),
                ).fetchall()
                for r in rows:
                    facts[r["id"]] = dict(r)
                    for end in (r["src"], r["dst"]):
                        if end not in seen:
                            seen.add(end)
                            nxt.add(end)
            frontier = nxt
        return list(facts.values())


def seed(g):
    g.upsert_node("person:alice", "Person", "Alice Chen", role="staff-engineer")
    g.upsert_node("design:redis", "Design", "Redis job queue")
    g.upsert_node("design:nats", "Design", "NATS job queue")
    g.upsert_node("adr:142", "ADR", "ADR-142 drop Redis")
    g.upsert_node("inc:queue-2024", "Incident", "queue-outage-2024")
    g.upsert_node("doc:pm", "Document", "postmortem.md")
    kw = dict(valid_from="2024-06-01", learned_at="2024-06-03", source="doc:pm")
    g.write_edge("design:nats", "supersedes", "design:redis", **kw)
    g.write_edge("adr:142", "decided_by", "person:alice", **kw)
    g.write_edge("adr:142", "caused_by", "inc:queue-2024", **kw)
    g.write_edge("design:nats", "decided_in", "adr:142", **kw)
    g.write_edge(
        "doc:pm",
        "mentions",
        "inc:queue-2024",
        valid_from="2024-06-03",
        learned_at="2024-06-03",
        source="doc:pm",
    )


@dataclass
class RunState:
    question: str
    intent: str | None = None
    memory_hits: list = field(default_factory=list)
    answer: str = ""
    notes: list = field(default_factory=list)


def classifier(state):
    q = state.question.lower()
    if any(w in q for w in ("why", "who decided", "supersede", "caused")):
        return {"intent": "multihop"}
    if any(w in q for w in ("what is", "where is")):
        return {"intent": "lookup"}
    return {"intent": "refuse"}


def memory_query(graph, as_of, max_hops=3, max_facts=8):
    """Chapter 4 node: code that reads G_K and writes a typed partial update."""

    def node(state):
        if state.intent == "refuse":
            return {"memory_hits": [], "notes": state.notes + ["memory_query skipped"]}
        seed_id = "design:nats"
        if "alice" in state.question.lower():
            seed_id = "person:alice"
        facts = graph.neighborhood(seed_id, hops=max_hops, day=as_of)
        slim = [
            {
                "src": f["src_name"],
                "predicate": f["predicate"],
                "dst": f["dst_name"],
                "valid_from": f["valid_from"],
                "valid_to": f["valid_to"],
                "source": f["source"],
            }
            for f in facts[:max_facts]
        ]
        return {"memory_hits": slim}

    return node


def reviewer(state):
    if not state.memory_hits:
        return {"answer": "No structured memory. Refuse to guess."}
    lines = [
        "%s -%s> %s (from %s to %s, source=%s)"
        % (
            h["src"],
            h["predicate"],
            h["dst"],
            h["valid_from"],
            h["valid_to"] or "open",
            h["source"],
        )
        for h in state.memory_hits
    ]
    return {"answer": "Structured memory, not similarity:\n" + "\n".join(lines)}


def apply(state, update):
    for k, v in update.items():
        setattr(state, k, v)
    return state


def run_execution_graph(question, graph, as_of):
    state = RunState(question=question)
    mq = memory_query(graph, as_of=as_of)
    for fn in (classifier, mq, reviewer):
        state = apply(state, fn(state))
    return state


def main():
    g = MemoryGraph("memory_graph.sqlite")
    seed(g)
    try:
        g.write_edge(
            "design:nats",
            "supersedes",
            "person:alice",
            valid_from="2024-06-01",
            learned_at="2024-06-03",
            source="doc:pm",
        )
    except ShapeError as exc:
        print("SHACL correctly refused a typed hallucination:", exc)
    now = date.today().isoformat()
    result = run_execution_graph("Why did we drop Redis for the job queue?", g, as_of=now)
    print("intent:", result.intent)
    print(result.answer)
    print("facts returned:", len(result.memory_hits))


if __name__ == "__main__":
    main()
