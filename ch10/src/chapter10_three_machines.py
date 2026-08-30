"""Same small execution graph, three machines.

Run: python chapter10_three_machines.py

No network. The 'LLM' is a stub that returns a verdict from state.
"""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Literal, Optional


@dataclass
class Brief:
    topic: str
    notes: Dict[str, str] = field(default_factory=dict)
    draft: str = ""
    verdict: Literal["", "pass", "fail"] = ""
    revise_count: int = 0
    log: List[str] = field(default_factory=list)

    def record(self, msg: str) -> None:
        self.log.append(msg)


def research_web(brief: Brief) -> None:
    brief.notes["web"] = f"web notes on {brief.topic}"
    brief.record("research_web")


def research_docs(brief: Brief) -> None:
    brief.notes["docs"] = f"docs notes on {brief.topic}"
    brief.record("research_docs")


def draft(brief: Brief) -> None:
    notes = " | ".join(brief.notes.values()) or "(no notes)"
    suffix = f" (revision {brief.revise_count})" if brief.revise_count else ""
    brief.draft = f"draft[{notes}]{suffix}"
    brief.record("draft")


def publish(brief: Brief) -> None:
    brief.record(f"publish: {brief.draft}")


class DagScheduler:
    def __init__(self, vertices: Iterable[str], edges: Iterable[tuple[str, str]]):
        self.vertices = list(vertices)
        self.succ: Dict[str, List[str]] = defaultdict(list)
        self.indeg: Dict[str, int] = {v: 0 for v in self.vertices}
        for u, v in edges:
            if u not in self.indeg or v not in self.indeg:
                raise ValueError(f"edge endpoint not in vertices: {(u, v)}")
            self.succ[u].append(v)
            self.indeg[v] += 1

    def topological_levels(self) -> List[List[str]]:
        indeg = dict(self.indeg)
        ready = deque([v for v, d in indeg.items() if d == 0])
        levels: List[List[str]] = []
        seen = 0
        while ready:
            level = list(ready)
            ready.clear()
            levels.append(level)
            seen += len(level)
            for u in level:
                for v in self.succ[u]:
                    indeg[v] -= 1
                    if indeg[v] == 0:
                        ready.append(v)
        if seen != len(self.vertices):
            raise ValueError("cycle detected; this scheduler requires a DAG")
        return levels


def _set_verdict_from_stub(brief: Brief) -> None:
    brief.verdict = "fail" if brief.revise_count == 0 else "pass"


def run_dag(topic: str) -> Brief:
    brief = Brief(topic=topic)
    vertices = [
        "intake",
        "research_web",
        "research_docs",
        "join",
        "draft",
        "review",
        "publish",
    ]
    edges = [
        ("intake", "research_web"),
        ("intake", "research_docs"),
        ("research_web", "join"),
        ("research_docs", "join"),
        ("join", "draft"),
        ("draft", "review"),
        ("review", "publish"),
    ]
    sched = DagScheduler(vertices, edges)
    impl: Dict[str, Callable[[Brief], None]] = {
        "intake": lambda b: b.record("intake"),
        "research_web": research_web,
        "research_docs": research_docs,
        "join": lambda b: b.record("join_all_of"),
        "draft": draft,
        "review": lambda b: (_set_verdict_from_stub(b), b.record(f"review:{b.verdict}")),
        "publish": publish,
    }
    for level in sched.topological_levels():
        for v in level:
            impl[v](brief)
    return brief


@dataclass
class FSM:
    state: str = "intake"
    k: int = 2

    def step(self, brief: Brief) -> Optional[str]:
        s = self.state
        if s == "intake":
            brief.record("intake")
            self.state = "researching"
        elif s == "researching":
            research_web(brief)
            research_docs(brief)
            brief.record("join_all_of")
            self.state = "drafting"
        elif s == "drafting":
            draft(brief)
            self.state = "reviewing"
        elif s == "reviewing":
            _set_verdict_from_stub(brief)
            brief.record(f"review:{brief.verdict}")
            if brief.verdict == "pass":
                self.state = "publishing"
            elif brief.revise_count < self.k:
                brief.revise_count += 1
                self.state = "drafting"  # back-edge
            else:
                self.state = "failed"
        elif s == "publishing":
            publish(brief)
            self.state = "end"
        elif s == "failed":
            brief.record("failed_closed")
            self.state = "end"
        elif s == "end":
            return "end"
        return self.state


def run_fsm(topic: str, k: int = 2) -> Brief:
    brief = Brief(topic=topic)
    machine = FSM(k=k)
    while machine.state != "end":
        machine.step(brief)
    return brief


ALLOWED_FROM_REVIEW = ("revise", "publish", "fail")


def stub_llm_route(brief: Brief) -> str:
    """Stand-in for a chat model that names the next node.

    The stub is deliberately slightly sloppy: it sometimes returns
    'ship_it', which is *not* in the allowlist, so the runtime's
    job (reject, do not invent a node) is visible in the log.
    """
    _set_verdict_from_stub(brief)
    if brief.verdict == "pass":
        return "ship_it"
    if brief.revise_count < 2:
        return "revise"
    return "fail"


def run_agent_graph(topic: str) -> Brief:
    brief = Brief(topic=topic)
    brief.record("intake")
    research_web(brief)
    research_docs(brief)
    brief.record("join_all_of")
    while True:
        draft(brief)
        proposed = stub_llm_route(brief)
        brief.record(f"llm_proposed:{proposed}")
        if proposed not in ALLOWED_FROM_REVIEW:
            brief.record(f"rejected_off_allowlist:{proposed}")
            next_node = (
                "publish"
                if brief.verdict == "pass"
                else ("revise" if brief.revise_count < 2 else "fail")
            )
        else:
            next_node = proposed
        if next_node == "publish":
            publish(brief)
            return brief
        if next_node == "fail":
            brief.record("failed_closed")
            return brief
        brief.revise_count += 1


if __name__ == "__main__":
    print("=== DAG (acyclic, no real revise) ===")
    d = run_dag("widget auth bug")
    print(" / ".join(d.log), "| verdict=", d.verdict)

    print("=== FSM (bounded cycle) ===")
    f = run_fsm("widget auth bug")
    print(" / ".join(f.log), "| verdict=", f.verdict, "| revises=", f.revise_count)

    print("=== Agent graph (stub LLM + allowlist) ===")
    a = run_agent_graph("widget auth bug")
    print(" / ".join(a.log), "| verdict=", a.verdict, "| revises=", a.revise_count)

    for bad in [("b", "a"), ("a", "b")]:
        try:
            DagScheduler(["a"], [bad])
            raise SystemExit(f"expected unknown endpoint {bad}")
        except ValueError:
            pass
