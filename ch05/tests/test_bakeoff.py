"""Behavioral tests for the Chapter 5 bakeoff listing."""
from loop_vs_graph_bakeoff import INCIDENT, RUBRIC, report, run_graph, run_loop


def test_loop_has_two_calls_and_no_state_copies() -> None:
    loop = run_loop(INCIDENT, RUBRIC, latency_s=0)
    assert loop.n_calls == 2
    assert loop.state_copies == 0
    assert "payments-api" in loop.output
    assert "PASS" in loop.output


def test_graph_has_three_calls_and_copies_state() -> None:
    graph = run_graph(INCIDENT, RUBRIC, latency_s=0)
    assert graph.n_calls == 3
    assert graph.state_copies > 0
    assert "PASS" in graph.output


def test_report_names_the_topology_tax() -> None:
    loop = run_loop(INCIDENT, RUBRIC, latency_s=0)
    graph = run_graph(INCIDENT, RUBRIC, latency_s=0)
    text = report(loop, graph)
    assert "did not harvest parallelism" in text
    assert graph.n_calls == loop.n_calls + 1
