"""Behavioral tests for the Chapter 8 doorway listing."""
from datetime import date

from memory_graph_node import ShapeError, MemoryGraph, seed, run_execution_graph


def test_shacl_refuses_design_supersedes_person() -> None:
    g = MemoryGraph(":memory:")
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
        assert "SHACL fail" in str(exc)
        return
    raise AssertionError("expected ShapeError")


def test_redis_question_returns_typed_hits() -> None:
    g = MemoryGraph(":memory:")
    seed(g)
    result = run_execution_graph(
        "Why did we drop Redis for the job queue?",
        g,
        as_of=date.today().isoformat(),
    )
    assert result.intent == "multihop"
    assert result.memory_hits
    assert "Structured memory" in result.answer
    assert any(h["predicate"] == "supersedes" for h in result.memory_hits)
