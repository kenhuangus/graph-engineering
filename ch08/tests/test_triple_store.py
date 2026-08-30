from __future__ import annotations

import pytest

from triple_store import TripleStore


RECORDS = [
    {"s": "Redis", "p": "superseded_by", "o": "Valkey", "provenance": "adr-14"},
    {"s": "adr-14", "p": "decided_by", "o": "Ken", "provenance": "adr-14"},
    {"s": "adr-14", "p": "caused_by", "o": "Incident-504", "provenance": "postmortem-88"},
    {"s": "Valkey", "p": "used_by", "o": "payments-api", "provenance": "runbook-2"},
    {"s": "payments-api", "p": "owned_by", "o": "Ken", "provenance": "org-chart"},
]


def populated() -> TripleStore:
    store = TripleStore()
    n = store.ingest(RECORDS)
    assert n == 5
    return store


def test_ingest_and_query() -> None:
    store = populated()
    hits = store.query(s="Redis")
    assert len(hits) == 1
    assert hits[0].p == "superseded_by"
    assert hits[0].o == "Valkey"
    by_pred = store.query(p="decided_by")
    assert [t.s for t in by_pred] == ["adr-14"]
    by_obj = store.query(o="Ken")
    assert {t.s for t in by_obj} == {"adr-14", "payments-api"}
    wildcard = store.query()
    assert len(wildcard) == 5


def test_provenance_retained() -> None:
    store = populated()
    triples = store.query(s="Redis", p="superseded_by", o="Valkey")
    assert len(triples) == 1
    assert triples[0].provenance == "adr-14"
    caused = store.query(p="caused_by")[0]
    assert caused.provenance == "postmortem-88"
    # Re-ingesting the same record does not drop provenance or duplicate.
    added = store.ingest([RECORDS[0]])
    assert added == 0
    assert store.query(s="Redis")[0].provenance == "adr-14"


def test_neighbor_walk_depth_1_and_2() -> None:
    store = populated()
    d1 = store.neighbors("Redis", depth=1)
    assert d1 == {"Valkey"}
    d2 = store.neighbors("Redis", depth=2)
    assert "Valkey" in d2
    assert "payments-api" in d2
    assert "Redis" not in d2
    ken1 = store.neighbors("Ken", depth=1)
    assert ken1 == {"adr-14", "payments-api"}
    with pytest.raises(ValueError):
        store.neighbors("Redis", depth=3)


def test_execute_raises_typeerror() -> None:
    store = populated()
    with pytest.raises(TypeError, match="knowledge graph"):
        store.execute("refund-workflow")
