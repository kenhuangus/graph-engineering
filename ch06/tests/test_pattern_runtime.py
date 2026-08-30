from __future__ import annotations

from pattern_runtime import (
    WORKERS,
    fanout_join,
    make_job,
    sequential_path,
    supervisor_star,
    worker_to_worker_messages,
)


def test_three_patterns_produce_different_traces() -> None:
    seq = sequential_path(make_job())
    star = supervisor_star(make_job())
    fan = fanout_join(make_job())
    seq_nodes = [(e.node, e.superstep) for e in seq.trace]
    star_nodes = [(e.node, e.superstep) for e in star.trace]
    fan_nodes = [(e.node, e.superstep) for e in fan.trace]
    assert seq_nodes != fan_nodes
    assert seq.messages != star.messages
    assert star.pattern != fan.pattern
    # Superstep occupancy differs: sequential has 4 steps, fanout joins researchers.
    seq_steps = {e.superstep for e in seq.trace}
    fan_steps = {e.superstep for e in fan.trace}
    assert len(seq_steps) == 4
    assert len(fan_steps) == 3


def test_sequential_order() -> None:
    result = sequential_path(make_job("topic-x"))
    names = [e.node for e in result.trace]
    assert names == ["classify", "research_web", "research_docs", "write"]
    for i, e in enumerate(result.trace):
        assert e.superstep == i
    assert "web" in result.job.notes
    assert "docs" in result.job.notes
    assert "topic-x" in result.job.document


def test_fanout_join_runs_both_researchers_before_write() -> None:
    result = fanout_join(make_job("join-me"))
    nodes = [e.node for e in result.trace]
    assert nodes.index("research_web") < nodes.index("write")
    assert nodes.index("research_docs") < nodes.index("write")
    web_ev = next(e for e in result.trace if e.node == "research_web")
    docs_ev = next(e for e in result.trace if e.node == "research_docs")
    write_ev = next(e for e in result.trace if e.node == "write")
    assert web_ev.superstep == docs_ev.superstep
    assert write_ev.superstep > web_ev.superstep
    assert "web" in result.job.notes and "docs" in result.job.notes
    assert "web notes on join-me" in result.job.document
    assert "docs notes on join-me" in result.job.document
    # Join completeness: write's snapshot already contains both notes.
    keys = dict(write_ev.notes_snapshot)
    assert "web" in keys and "docs" in keys


def test_supervisor_never_lets_workers_message_each_other() -> None:
    result = supervisor_star(make_job())
    leaked = worker_to_worker_messages(result)
    assert leaked == []
    # Every dispatch and report goes through the supervisor.
    worker_msgs = [m for m in result.messages if m.src in WORKERS or m.dst in WORKERS]
    assert worker_msgs, "supervisor must actually dispatch"
    for m in worker_msgs:
        endpoints = {m.src, m.dst}
        assert "supervisor" in endpoints
        assert not (m.src in WORKERS and m.dst in WORKERS)
    names = [e.node for e in result.trace]
    assert set(names) == WORKERS
