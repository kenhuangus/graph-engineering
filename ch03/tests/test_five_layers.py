from __future__ import annotations

from five_layers import SystemDescription, score_layers


def test_react_loop_scores_loop_highest() -> None:
    desc = SystemDescription(
        has_system_prompt=True,
        single_turn=False,
        window_curation=False,
        retrieved_chunks_in_window=0,
        observe_act_verify=True,
        inner_loop_retries=6,
        tool_calls_inside_one_worker=True,
        named_nodes=("agent",),
        named_edges=(),
        fan_out=False,
        join=False,
        halt_node=False,
        persistent_store=False,
        triple_retrieval=False,
    )
    result = score_layers(desc)
    assert result.primary == "loop"
    assert result.scores["loop"] > result.scores["graph"]
    assert result.scores["loop"] > result.scores["prompt"]
    assert result.scores["loop"] > result.scores["memory"]
    assert 0.0 <= result.scores["loop"] <= 1.0


def test_fanout_dag_scores_graph_highest() -> None:
    nodes = ("plan", "worker_a", "worker_b", "worker_c", "join", "halt")
    edges = (
        ("plan", "worker_a"),
        ("plan", "worker_b"),
        ("plan", "worker_c"),
        ("worker_a", "join"),
        ("worker_b", "join"),
        ("worker_c", "join"),
        ("join", "halt"),
    )
    desc = SystemDescription(
        has_system_prompt=True,
        single_turn=False,
        observe_act_verify=False,
        inner_loop_retries=0,
        tool_calls_inside_one_worker=False,
        named_nodes=nodes,
        named_edges=edges,
        fan_out=True,
        join=True,
        halt_node=True,
        persistent_store=False,
        triple_retrieval=False,
    )
    result = score_layers(desc)
    assert result.primary == "graph"
    assert result.scores["graph"] > result.scores["loop"]
    assert result.scores["graph"] > result.scores["memory"]
    assert result.scores["graph"] > result.scores["prompt"]


def test_triplestore_rag_scores_memory_highest() -> None:
    desc = SystemDescription(
        has_system_prompt=True,
        single_turn=True,
        window_curation=False,
        retrieved_chunks_in_window=0,
        observe_act_verify=False,
        named_nodes=("retrieve", "generate"),
        named_edges=(("retrieve", "generate"),),
        fan_out=False,
        join=False,
        halt_node=False,
        persistent_store=True,
        triple_retrieval=True,
        provenance_on_facts=True,
        entity_types=("Person", "Design", "ADR", "Incident"),
    )
    result = score_layers(desc)
    assert result.primary == "memory"
    assert result.scores["memory"] > result.scores["graph"]
    assert result.scores["memory"] > result.scores["context"]
    assert result.scores["memory"] > result.scores["prompt"]


def test_all_scores_are_unit_interval() -> None:
    desc = SystemDescription(
        has_system_prompt=True,
        single_turn=True,
        window_curation=True,
        retrieved_chunks_in_window=8,
        observe_act_verify=True,
        inner_loop_retries=3,
        tool_calls_inside_one_worker=True,
        named_nodes=("a", "b", "c"),
        named_edges=(("a", "b"), ("b", "c")),
        fan_out=True,
        join=True,
        halt_node=True,
        persistent_store=True,
        triple_retrieval=True,
        provenance_on_facts=True,
        entity_types=("Person",),
    )
    result = score_layers(desc)
    assert set(result.scores) == {"prompt", "context", "loop", "graph", "memory"}
    for name, value in result.scores.items():
        assert 0.0 <= value <= 1.0, name


def test_chunk_stuffing_is_context_not_memory() -> None:
    desc = SystemDescription(
        has_system_prompt=True,
        single_turn=True,
        window_curation=True,
        retrieved_chunks_in_window=12,
        persistent_store=False,
        triple_retrieval=False,
    )
    result = score_layers(desc)
    assert result.primary == "context"
    assert result.scores["context"] > result.scores["memory"]
