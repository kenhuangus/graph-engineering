"""Authorization graph + reachability check. Companion:

chapter11_authz_reachability.py

Run: python3 chapter11_authz_reachability.py
"""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Principal:
    name: str
    kind: str  # human | agent | tool | service


@dataclass
class AuthzGraph:
    nodes: set[str]
    edges: set[tuple[str, str]]
    start: str
    principals: dict[str, Principal]
    node_tools: dict[str, set[str]] = field(default_factory=dict)
    sensitive_actions: set[str] = field(default_factory=set)
    approval_nodes: set[str] = field(default_factory=set)
    sensitive_tools: set[str] = field(
        default_factory=lambda: {"issue_refund", "wire_payment", "apply_patch"}
    )

    def _succ(self) -> dict[str, set[str]]:
        s: dict[str, set[str]] = defaultdict(set)
        for u, v in self.edges:
            if u not in self.nodes or v not in self.nodes:
                raise KeyError(f"edge ({u!r}, {v!r}) mentions an unknown node")
            s[u].add(v)
        return dict(s)

    def paths(self, src: str, dst: str) -> list[list[str]]:
        succ = self._succ()
        found: list[list[str]] = []

        def dfs(node: str, trail: list[str], seen: set[str]) -> None:
            if node == dst:
                found.append(trail[:])
                return
            for nxt in sorted(succ.get(node, ())):
                if nxt in seen:
                    continue
                trail.append(nxt)
                seen.add(nxt)
                dfs(nxt, trail, seen)
                seen.remove(nxt)
                trail.pop()

        dfs(src, [src], {src})
        return found

    def ungated_paths(self, action: str) -> list[list[str]]:
        if action not in self.nodes:
            raise KeyError(action)
        out: list[list[str]] = []
        for path in self.paths(self.start, action):
            if not any(n in self.approval_nodes for n in path[:-1]):
                out.append(path)
        return out

    def is_gated(self, action: str) -> bool:
        return bool(self.paths(self.start, action)) and not self.ungated_paths(action)

    def blast_radius(self, compromised: str) -> set[str]:
        succ = self._succ()
        seen = {compromised}
        q = deque([compromised])
        while q:
            u = q.popleft()
            for v in succ.get(u, ()):
                if v not in seen:
                    seen.add(v)
                    q.append(v)
        return seen

    def findings(self) -> list[str]:
        notes: list[str] = []
        for action in sorted(self.sensitive_actions):
            if action not in self.nodes:
                notes.append(f"missing-node: {action}")
                continue
            if not self.paths(self.start, action):
                notes.append(f"unreachable: {action}")
                continue
            ungated = self.ungated_paths(action)
            if ungated:
                notes.append(
                    f"bypass: {action} has {len(ungated)} ungated path(s); "
                    f"example: {' → '.join(ungated[0])}"
                )
            else:
                notes.append(f"gated: {action} requires an approval node on every path")
        for node, tools in sorted(self.node_tools.items()):
            bad = tools & self.sensitive_tools
            if bad and node not in self.approval_nodes | self.sensitive_actions:
                notes.append(
                    f"tool-smuggle: {node} holds {sorted(bad)} but is not a gated action"
                )
        return notes


def _principals() -> dict[str, Principal]:
    return {
        "ken": Principal("ken", "human"),
        "analyst": Principal("analyst", "agent"),
        "refund": Principal("refund", "agent"),
        "stripe": Principal("stripe", "service"),
    }


def governed_refund() -> AuthzGraph:
    return AuthzGraph(
        nodes={
            "START",
            "fetch_history",
            "analyze_complaint",
            "human_approval",
            "issue_refund",
        },
        edges={
            ("START", "fetch_history"),
            ("fetch_history", "analyze_complaint"),
            ("analyze_complaint", "human_approval"),
            ("human_approval", "issue_refund"),
        },
        start="START",
        principals=_principals(),
        node_tools={"issue_refund": {"issue_refund"}},
        sensitive_actions={"issue_refund"},
        approval_nodes={"human_approval"},
    )


def bypass_refund() -> AuthzGraph:
    g = governed_refund()
    g.edges = set(g.edges)
    g.edges.add(("analyze_complaint", "issue_refund"))
    return g


def fanout_blast() -> AuthzGraph:
    return AuthzGraph(
        nodes={"START", "scout", "apply", "halt"},
        edges={
            ("START", "scout"),
            ("scout", "apply"),
            ("apply", "halt"),
        },
        start="START",
        principals=_principals(),
        node_tools={"apply": {"apply_patch"}},
        sensitive_actions={"apply"},
        approval_nodes=set(),
    )


if __name__ == "__main__":
    gov = governed_refund()
    assert gov.is_gated("issue_refund"), gov.findings()
    assert "issue_refund" in gov.blast_radius("analyze_complaint")
    assert any(n.startswith("gated:") for n in gov.findings())

    bypass = bypass_refund()
    assert not bypass.is_gated("issue_refund"), bypass.findings()
    notes = bypass.findings()
    assert any("bypass:" in n for n in notes)
    assert any("START → fetch_history → analyze_complaint → issue_refund" in n for n in notes)

    fan = fanout_blast()
    assert "apply" in fan.blast_radius("scout")
    assert any("bypass:" in n for n in fan.findings())
    print("ok", gov.findings()[0])
    print("ok", [n for n in notes if n.startswith("bypass:")][0])
    print("ok blast", sorted(fan.blast_radius("scout")))
