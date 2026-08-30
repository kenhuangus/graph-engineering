"""Chapter 8 — knowledge graph as memory, not as a workflow.

Ingest records into (s, p, o) triples with provenance. Query by s / p / o
with None as wildcard. Neighbor walk of depth 1 or 2. Refuse execute() —
this store is not an orchestrator.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator, Sequence


@dataclass(frozen=True)
class Triple:
    s: str
    p: str
    o: str
    provenance: str


class TripleStore:
    def __init__(self) -> None:
        self._triples: list[Triple] = []

    def ingest(self, records: Sequence[dict[str, str]]) -> int:
        """Ingest dicts with keys s/p/o/provenance (aliases subject/predicate/object/source allowed).

        Returns the number of triples added. Duplicate (s,p,o,provenance) rows are skipped.
        """
        existing = {(t.s, t.p, t.o, t.provenance) for t in self._triples}
        added = 0
        for rec in records:
            s = rec.get("s") or rec.get("subject")
            p = rec.get("p") or rec.get("predicate")
            o = rec.get("o") or rec.get("object")
            prov = rec.get("provenance") or rec.get("source") or rec.get("prov") or ""
            if not s or not p or not o:
                raise ValueError(f"record is missing s/p/o: {rec!r}")
            if not prov:
                raise ValueError(f"record is missing provenance: {rec!r}")
            key = (s, p, o, prov)
            if key in existing:
                continue
            existing.add(key)
            self._triples.append(Triple(s=s, p=p, o=o, provenance=prov))
            added += 1
        return added

    def query(
        self,
        s: str | None = None,
        p: str | None = None,
        o: str | None = None,
    ) -> list[Triple]:
        """Wildcard query: None matches any binding."""
        out: list[Triple] = []
        for t in self._triples:
            if s is not None and t.s != s:
                continue
            if p is not None and t.p != p:
                continue
            if o is not None and t.o != o:
                continue
            out.append(t)
        return out

    def neighbors(self, node: str, depth: int = 1) -> set[str]:
        """Undirected neighbor walk. `depth` must be 1 or 2. Excludes `node` itself."""
        if depth not in (1, 2):
            raise ValueError("depth must be 1 or 2")
        adj: dict[str, set[str]] = {}
        for t in self._triples:
            adj.setdefault(t.s, set()).add(t.o)
            adj.setdefault(t.o, set()).add(t.s)

        frontier = {node}
        seen: set[str] = {node}
        reached: set[str] = set()
        for _ in range(depth):
            nxt: set[str] = set()
            for u in frontier:
                for v in adj.get(u, ()):
                    if v not in seen:
                        seen.add(v)
                        reached.add(v)
                        nxt.add(v)
            frontier = nxt
        return reached

    def execute(self, *args: object, **kwargs: object) -> None:
        """A knowledge graph is not a workflow. There is nothing to execute."""
        raise TypeError(
            "TripleStore.execute() refused: this is a knowledge graph (G_K), "
            "not an execution graph. Query it; do not run it."
        )

    def __len__(self) -> int:
        return len(self._triples)
