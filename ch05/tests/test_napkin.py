from __future__ import annotations

from napkin import Decision, JobSpec, REASONS, napkin_test


def test_one_worker_plus_tools_stays_on_loop() -> None:
    job = JobSpec(
        workers=1,
        tools=("search", "fetch", "write_file"),
        specialties=("coder",),
        fanout=False,
        fanout_cardinality_known=None,
        typed_handoffs=False,
        human_interrupt=False,
        halt_contract=False,
    )
    decision = napkin_test(job)
    assert decision.action == "stay_on_loop"
    assert decision.reasons == ()
    assert isinstance(decision, Decision)


def test_unknown_fanout_cardinality_builds_graph() -> None:
    job = JobSpec(
        workers=1,
        tools=("search",),
        specialties=("scout",),
        fanout=True,
        fanout_cardinality_known=False,
        typed_handoffs=False,
        human_interrupt=False,
        halt_contract=False,
    )
    decision = napkin_test(job)
    assert decision.action == "build_graph"
    assert "unknown_cardinality" in decision.reasons
    assert set(decision.reasons) <= REASONS


def test_mixed_fanout_handoff_interrupt_builds_graph() -> None:
    job = JobSpec(
        workers=3,
        tools=("search", "docs"),
        specialties=("classify", "research", "write"),
        fanout=True,
        fanout_cardinality_known=True,
        typed_handoffs=True,
        human_interrupt=True,
        halt_contract=True,
    )
    decision = napkin_test(job)
    assert decision.action == "build_graph"
    assert "needs_fanout" in decision.reasons
    assert "typed_handoff" in decision.reasons
    assert "human_interrupt" in decision.reasons
    assert "halt_contract" in decision.reasons
    assert "unknown_cardinality" not in decision.reasons
    for r in decision.reasons:
        assert r in REASONS


def test_reasons_are_closed_set() -> None:
    job = JobSpec(workers=2, specialties=("a", "b"), typed_handoffs=True)
    decision = napkin_test(job)
    assert decision.action == "build_graph"
    assert set(decision.reasons) <= REASONS
    assert set(decision.reasons)  # non-empty
