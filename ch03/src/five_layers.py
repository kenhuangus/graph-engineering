"""Chapter 3 — score a system against the five sibling layers.

Harness engineering is the paradigm. Prompt, context, loop, graph, and
memory are siblings, not rungs. This scorer does not parse prose: it reads
structured fields and returns a 0-1 score per layer plus the layer that is
actually doing the work (argmax, with documented tie-breaks).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Layer = Literal["prompt", "context", "loop", "graph", "memory"]
LAYERS: tuple[Layer, ...] = ("prompt", "context", "loop", "graph", "memory")


@dataclass(frozen=True)
class SystemDescription:
    """Structured description of a system. Fill booleans and counts; no NLP."""

    has_system_prompt: bool = False
    single_turn: bool = False
    window_curation: bool = False
    retrieved_chunks_in_window: int = 0
    observe_act_verify: bool = False
    inner_loop_retries: int = 0
    tool_calls_inside_one_worker: bool = False
    named_nodes: tuple[str, ...] = ()
    named_edges: tuple[tuple[str, str], ...] = ()
    fan_out: bool = False
    join: bool = False
    halt_node: bool = False
    persistent_store: bool = False
    triple_retrieval: bool = False
    provenance_on_facts: bool = False
    entity_types: tuple[str, ...] = ()


@dataclass(frozen=True)
class LayerScore:
    primary: Layer
    scores: dict[str, float]  # each in [0, 1]


def _clip(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def score_layers(desc: SystemDescription) -> LayerScore:
    """Return per-layer scores in [0, 1] and the layer doing the work.

    Tie-break if two scores are equal: graph > loop > memory > context > prompt.
    That order matches the book's subject (topology) without turning the
    siblings into a replacement ladder — it only breaks ties.
    """
    scores: dict[str, float] = {layer: 0.0 for layer in LAYERS}

    # Prompt: a single-turn instruction is the unit of control.
    prompt = 0.0
    if desc.has_system_prompt:
        prompt += 0.35
    if desc.single_turn:
        prompt += 0.45
    if len(desc.named_nodes) <= 1 and not desc.fan_out and not desc.observe_act_verify:
        prompt += 0.20
    scores["prompt"] = _clip(prompt)

    # Context: the window is the unit of control.
    context = 0.0
    if desc.window_curation:
        context += 0.45
    if desc.retrieved_chunks_in_window > 0:
        context += min(0.40, 0.10 * desc.retrieved_chunks_in_window)
    if desc.single_turn and desc.retrieved_chunks_in_window > 0:
        context += 0.15
    scores["context"] = _clip(context)

    # Loop: observe-act-verify inside one worker.
    loop = 0.0
    if desc.observe_act_verify:
        loop += 0.50
    if desc.tool_calls_inside_one_worker:
        loop += 0.20
    if desc.inner_loop_retries > 0:
        loop += min(0.30, 0.06 * desc.inner_loop_retries)
    # A one-node "graph" is still a loop.
    if len(desc.named_nodes) <= 1 and desc.observe_act_verify:
        loop += 0.15
    if desc.fan_out or desc.join:
        loop -= 0.25
    scores["loop"] = _clip(loop)

    # Graph: named topology with fan-out / join / halt.
    graph = 0.0
    n_nodes = len(desc.named_nodes)
    n_edges = len(desc.named_edges)
    if n_nodes >= 2:
        graph += 0.25
    if n_nodes >= 4:
        graph += 0.15
    if n_edges >= 1:
        graph += 0.10
    if desc.fan_out:
        graph += 0.25
    if desc.join:
        graph += 0.20
    if desc.halt_node:
        graph += 0.10
    if n_nodes <= 1 and not desc.fan_out:
        graph -= 0.20
    scores["graph"] = _clip(graph)

    # Memory: a store of facts, not a window stuffing.
    memory = 0.0
    if desc.persistent_store:
        memory += 0.35
    if desc.triple_retrieval:
        memory += 0.35
    if desc.provenance_on_facts:
        memory += 0.15
    if desc.entity_types:
        memory += min(0.20, 0.05 * len(desc.entity_types))
    # A RAG that is only chunk stuffing is context, not memory topology.
    if desc.triple_retrieval and desc.persistent_store:
        memory += 0.10
    if desc.retrieved_chunks_in_window > 0 and not desc.triple_retrieval:
        memory -= 0.15
    scores["memory"] = _clip(memory)

    tie_rank = {"graph": 0, "loop": 1, "memory": 2, "context": 3, "prompt": 4}
    primary = min(LAYERS, key=lambda layer: (-scores[layer], tie_rank[layer]))
    return LayerScore(primary=primary, scores=scores)
