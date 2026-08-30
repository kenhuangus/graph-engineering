from __future__ import annotations

import pytest

from graph_kinds import (
    REASON_KG_CONTROL_FLOW,
    REASON_KG_NODES_RUN,
    REASON_TRACE_AS_MEMORY,
    REASON_WORKFLOW_RDF,
    GraphObject,
    MashupError,
    classify,
)


def test_execution_graph_accepted() -> None:
    obj = GraphObject(
        name="refund-workflow",
        node_kinds=("agent", "tool", "evaluator", "human"),
        edge_kinds=("unconditional", "conditional", "dynamic"),
        nodes_do_work=True,
        edges_are_facts=False,
        persists_beyond_run=False,
        is_one_run_recording=False,
        nodes_run=True,
    )
    result = classify(obj)
    assert result.kind == "execution_graph"
    assert result.name == "refund-workflow"


def test_knowledge_graph_accepted() -> None:
    obj = GraphObject(
        name="incident-memory",
        node_kinds=("entity", "person", "document"),
        edge_kinds=("supersedes", "prov:wasDerivedFrom"),
        nodes_do_work=False,
        edges_are_facts=True,
        persists_beyond_run=True,
        is_one_run_recording=False,
        nodes_run=False,
    )
    result = classify(obj)
    assert result.kind == "knowledge_graph"


def test_run_trace_accepted() -> None:
    obj = GraphObject(
        name="ticket-8841-trace",
        node_kinds=("span", "llm_call"),
        edge_kinds=("happened_before", "span_child"),
        nodes_do_work=False,
        edges_are_facts=False,
        persists_beyond_run=False,
        is_one_run_recording=True,
        nodes_run=False,
    )
    result = classify(obj)
    assert result.kind == "run_trace"


def test_mashup_workflow_with_rdf_edges_rejected() -> None:
    obj = GraphObject(
        name="workflow-as-rdf",
        node_kinds=("agent", "tool"),
        edge_kinds=("rdf:type", "rdfs:subClassOf"),
        nodes_do_work=True,
        edges_are_facts=True,
        persists_beyond_run=False,
        is_one_run_recording=False,
        nodes_run=True,
    )
    with pytest.raises(MashupError) as ei:
        classify(obj)
    assert ei.value.reason_code == REASON_WORKFLOW_RDF


def test_mashup_kg_whose_nodes_run_rejected() -> None:
    obj = GraphObject(
        name="kg-that-runs",
        node_kinds=("entity", "person"),
        edge_kinds=("supersedes",),
        nodes_do_work=False,
        edges_are_facts=True,
        persists_beyond_run=True,
        is_one_run_recording=False,
        nodes_run=True,
    )
    with pytest.raises(MashupError) as ei:
        classify(obj)
    assert ei.value.reason_code == REASON_KG_NODES_RUN


def test_mashup_trace_claimed_as_memory_rejected() -> None:
    obj = GraphObject(
        name="chat-log-as-kg",
        node_kinds=("span",),
        edge_kinds=("happened_before",),
        nodes_do_work=False,
        edges_are_facts=True,
        persists_beyond_run=True,
        is_one_run_recording=True,
        nodes_run=False,
    )
    with pytest.raises(MashupError) as ei:
        classify(obj)
    assert ei.value.reason_code == REASON_TRACE_AS_MEMORY


def test_mashup_kg_with_control_flow_edges_rejected() -> None:
    obj = GraphObject(
        name="kg-with-next-edges",
        node_kinds=("entity",),
        edge_kinds=("control_flow", "next"),
        nodes_do_work=False,
        edges_are_facts=False,
        persists_beyond_run=True,
        is_one_run_recording=False,
        nodes_run=False,
    )
    with pytest.raises(MashupError) as ei:
        classify(obj)
    assert ei.value.reason_code == REASON_KG_CONTROL_FLOW
