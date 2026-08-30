"""Chapter 13 — check a run trace against a spec.

Invariants:
  - halt reached
  - all-of join completed before downstream
  - no unconstrained_spend (a spend node without a prior gate node)
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence


HALT_NOT_REACHED = "halt_not_reached"
JOIN_INCOMPLETE = "join_incomplete"
UNCONSTRAINED_SPEND = "unconstrained_spend"


@dataclass(frozen=True)
class TraceEvent:
    node: str
    status: str = "ok"  # ok | skipped | failed


@dataclass(frozen=True)
class JoinSpec:
    """All of `required` must appear in the trace before `downstream`."""

    name: str
    required: tuple[str, ...]
    downstream: str


@dataclass(frozen=True)
class TraceSpec:
    halt: str
    joins: tuple[JoinSpec, ...] = ()
    gate_nodes: tuple[str, ...] = ()
    spend_nodes: tuple[str, ...] = ()


@dataclass(frozen=True)
class Violation:
    code: str
    message: str
    node: str | None = None


def _nodes_in_order(trace: Sequence[TraceEvent | dict | str]) -> list[str]:
    names: list[str] = []
    for item in trace:
        if isinstance(item, TraceEvent):
            names.append(item.node)
        elif isinstance(item, dict):
            names.append(str(item["node"]))
        else:
            names.append(str(item))
    return names


def check_trace(trace: Sequence[TraceEvent | dict | str], spec: TraceSpec) -> list[Violation]:
    """Return invariant violations. Empty list means the trace is legal."""
    names = _nodes_in_order(trace)
    violations: list[Violation] = []

    if spec.halt not in names:
        violations.append(
            Violation(
                code=HALT_NOT_REACHED,
                message=f"halt node {spec.halt!r} never appears in the trace",
                node=spec.halt,
            )
        )

    index = {name: i for i, name in enumerate(names)}  # last-write: first occurrence used below
    first_index: dict[str, int] = {}
    for i, name in enumerate(names):
        first_index.setdefault(name, i)

    for join in spec.joins:
        down_i = first_index.get(join.downstream)
        if down_i is None:
            # Downstream never ran — not a skip-join failure by itself.
            continue
        missing: list[str] = []
        late: list[str] = []
        for req in join.required:
            req_i = first_index.get(req)
            if req_i is None:
                missing.append(req)
            elif req_i >= down_i:
                late.append(req)
        if missing or late:
            violations.append(
                Violation(
                    code=JOIN_INCOMPLETE,
                    message=(
                        f"join {join.name!r}: downstream {join.downstream!r} ran at {down_i} "
                        f"before required {join.required!r} "
                        f"(missing={missing}, late={late})"
                    ),
                    node=join.downstream,
                )
            )

    gate_set = set(spec.gate_nodes)
    for spend in spec.spend_nodes:
        spend_i = first_index.get(spend)
        if spend_i is None:
            continue
        prior = names[:spend_i]
        if not any(n in gate_set for n in prior):
            violations.append(
                Violation(
                    code=UNCONSTRAINED_SPEND,
                    message=f"spend node {spend!r} ran with no prior gate in {spec.gate_nodes!r}",
                    node=spend,
                )
            )

    return violations
