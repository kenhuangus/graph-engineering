"""Behavioral tests for the Chapter 10 three-machines listing."""
from chapter10_three_machines import DagScheduler, run_agent_graph, run_dag, run_fsm


def test_dag_has_no_revise_back_edge():
    brief = run_dag("widget auth bug")
    assert "publish:" in " ".join(brief.log)
    assert brief.revise_count == 0


def test_fsm_takes_the_back_edge_once():
    brief = run_fsm("widget auth bug")
    assert brief.revise_count == 1
    assert brief.verdict == "pass"
    assert any(line.startswith("publish:") for line in brief.log)


def test_agent_rejects_ship_it():
    brief = run_agent_graph("widget auth bug")
    joined = " ".join(brief.log)
    assert "rejected_off_allowlist:ship_it" in joined
    assert "publish:" in joined


def test_unknown_endpoint_is_compile_error():
    try:
        DagScheduler(["a"], [("b", "a")])
    except ValueError:
        return
    raise AssertionError("expected ValueError")
