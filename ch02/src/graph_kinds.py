"""Chapter 2 — classify a GraphObject as G_A, G_K, or a run trace.

An execution graph (G_A) is a topology of work: nodes do work, edges route a
run. A knowledge graph (G_K) is a topology of facts: nodes are entities,
edges are typed relations with optional provenance. A run_trace records what
one run actually fired; it is not the declared topology and it is not memory.

Mash-ups (a workflow whose edges are RDF relations, a KG whose nodes run,
a trace that claims to persist as facts) are rejected with a reason code.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Kind = Literal["execution_graph", "knowledge_graph", "run_trace"]

REASON_WORKFLOW_RDF = "workflow_with_rdf_edges"
REASON_KG_NODES_RUN = "kg_nodes_run"
REASON_TRACE_AS_MEMORY = "trace_claimed_as_memory"
REASON_WORKFLOW_ENTITIES = "workflow_nodes_are_entities"
REASON_KG_CONTROL_FLOW = "kg_edges_are_control_flow"

RDF_EDGE_MARKERS = frozenset({
    "rdf", "rdfs", "owl", "prov", "skos",
    "rdf:type", "rdfs:subClassOf", "owl:sameAs",
    "prov:wasDerivedFrom", "supersedes", "type_of",
})
WORK_NODE_MARKERS = frozenset({
    "agent", "tool", "evaluator", "human", "function", "llm", "router",
})
ENTITY_NODE_MARKERS = frozenset({
    "entity", "person", "organization", "document", "concept", "literal",
})
CONTROL_EDGE_MARKERS = frozenset({
    "control_flow", "unconditional", "conditional", "dynamic", "send",
    "next", "fanout", "fanin",
})
TRACE_EDGE_MARKERS = frozenset({
    "happened_before", "fired_then", "caused_call", "span_child",
})


class MashupError(ValueError):
    """Raised when a GraphObject mixes two of the three rooms."""

    def __init__(self, reason_code: str, message: str = "") -> None:
        self.reason_code = reason_code
        super().__init__(message or reason_code)


@dataclass(frozen=True)
class GraphObject:
    """Structured record — not free text. Fill the fields; do not parse prose."""

    name: str
    node_kinds: tuple[str, ...]
    edge_kinds: tuple[str, ...]
    nodes_do_work: bool
    edges_are_facts: bool
    persists_beyond_run: bool
    is_one_run_recording: bool
    nodes_run: bool = False  # "run" as in execute a step, not "exist"


@dataclass(frozen=True)
class Classification:
    kind: Kind
    name: str


def _has_overlap(values: tuple[str, ...], markers: frozenset[str]) -> bool:
    lowered = {v.lower() for v in values}
    return bool(lowered & {m.lower() for m in markers})


def classify(obj: GraphObject) -> Classification:
    """Return the kind, or raise MashupError with a reason_code."""
    rdf_edges = obj.edges_are_facts or _has_overlap(obj.edge_kinds, RDF_EDGE_MARKERS)
    control_edges = _has_overlap(obj.edge_kinds, CONTROL_EDGE_MARKERS)
    trace_edges = obj.is_one_run_recording or _has_overlap(obj.edge_kinds, TRACE_EDGE_MARKERS)
    work_nodes = obj.nodes_do_work or _has_overlap(obj.node_kinds, WORK_NODE_MARKERS)
    entity_nodes = _has_overlap(obj.node_kinds, ENTITY_NODE_MARKERS)
    nodes_run = obj.nodes_run

    # --- mash-ups (checked before accepting a clean class) -----------------
    if (work_nodes or obj.nodes_do_work) and rdf_edges and not obj.is_one_run_recording:
        # A workflow whose edges are RDF relations.
        raise MashupError(
            REASON_WORKFLOW_RDF,
            "execution topology cannot use RDF/fact edges as control flow",
        )
    if (entity_nodes or obj.persists_beyond_run) and nodes_run and not obj.nodes_do_work:
        raise MashupError(
            REASON_KG_NODES_RUN,
            "knowledge-graph nodes are entities; they do not run",
        )
    if nodes_run and obj.edges_are_facts and not obj.nodes_do_work:
        raise MashupError(
            REASON_KG_NODES_RUN,
            "knowledge-graph nodes are entities; they do not run",
        )
    if obj.is_one_run_recording and obj.persists_beyond_run and obj.edges_are_facts:
        raise MashupError(
            REASON_TRACE_AS_MEMORY,
            "a run trace is not a knowledge graph; it does not persist as facts",
        )
    if obj.nodes_do_work and entity_nodes and not obj.edges_are_facts:
        raise MashupError(
            REASON_WORKFLOW_ENTITIES,
            "execution-graph nodes do work; they are not KG entities",
        )
    if entity_nodes and control_edges and not obj.nodes_do_work:
        raise MashupError(
            REASON_KG_CONTROL_FLOW,
            "knowledge-graph edges are relations, not control flow",
        )

    # --- clean classes -----------------------------------------------------
    if obj.is_one_run_recording and not obj.persists_beyond_run:
        return Classification(kind="run_trace", name=obj.name)

    if (
        (entity_nodes or obj.edges_are_facts or obj.persists_beyond_run)
        and not obj.nodes_do_work
        and not nodes_run
        and not obj.is_one_run_recording
    ):
        return Classification(kind="knowledge_graph", name=obj.name)

    if obj.nodes_do_work and not obj.edges_are_facts and not obj.is_one_run_recording:
        return Classification(kind="execution_graph", name=obj.name)

    raise MashupError(
        REASON_WORKFLOW_RDF,
        "record does not sit cleanly in G_A, G_K, or run_trace",
    )
