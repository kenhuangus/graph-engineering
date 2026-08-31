"""Three specialized workers plus synthesis, via explicit messages.

Save as ch06_workers_messages.py and run: python ch06_workers_messages.py
No API keys. No framework. Nobody mutates a shared dict.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Message:
    """A typed, immutable payload handed across an edge."""

    kind: str
    sender: str
    body: Any
    schema: str = "chapter6.v1"


@dataclass
class Brief:
    title: str
    claims: list[str]
    caveats: list[str]
    holes: list[str]
    citations: list[str]


PACKET = {
    "topic": "multi-agent research systems",
    "sources": [
        {
            "id": "anthropic-2025-06",
            "text": (
                "Anthropic's Research feature uses an orchestrator-worker "
                "pattern. A multi-agent system with Opus 4 lead and Sonnet 4 "
                "subagents outperformed single-agent Opus 4 by 90.2 percent "
                "on an internal research eval. Multi-agent systems used about "
                "15x more tokens than chats. Coding is often a poor fit."
            ),
        },
        {
            "id": "cognition-2025-06",
            "text": (
                "Cognition argued in Don't Build Multi-Agents that parallel "
                "writers make implicit decisions that conflict. Default to a "
                "single-threaded agent. Share full traces. Actions carry "
                "implicit decisions."
            ),
        },
        {
            "id": "deepmind-mit-2026-01",
            "text": (
                "A 180-configuration sweep found centralized coordination "
                "improved parallelizable financial reasoning by 80.9 percent, "
                "while every multi-agent variant degraded sequential planning "
                "by 39 to 70 percent. Independent agents amplified errors 17.2x."
            ),
        },
    ],
}


def claim_miner(msg: Message) -> Message:
    if msg.kind != "packet" or msg.schema != "chapter6.v1":
        raise ValueError(f"claim_miner rejected {msg.kind}/{msg.schema}")
    packet = msg.body
    claims: list[str] = []
    for src in packet["sources"]:
        text = src["text"]
        for sentence in text.split(". "):
            s = sentence.strip().rstrip(".")
            if any(
                key in s.lower()
                for key in ("outperformed", "used about", "argued", "found", "amplified")
            ):
                claims.append(s)
    return Message(kind="claims", sender="claim_miner", body={"claims": claims})


def skeptic(msg: Message) -> Message:
    if msg.kind != "packet":
        raise ValueError(f"skeptic rejected {msg.kind}")
    packet = msg.body
    caveats: list[str] = []
    joined = " ".join(src["text"] for src in packet["sources"]).lower()
    if "15x" in joined or "15 x" in joined:
        caveats.append(
            "The 15x token multiple is versus chat, not versus a well-designed "
            "single agent; do not quote it as the cost of adding one worker."
        )
    if "coding is often a poor fit" in joined:
        caveats.append(
            "Breadth-first research is the published fit; do not transplant "
            "the topology onto a tightly coupled coding task."
        )
    if "don't build" in joined or "single-threaded" in joined:
        caveats.append(
            "Cognition's ban was aimed at parallel writers, not at readonly "
            "research subagents. The later post still rejects unstructured swarms."
        )
    if "every multi-agent variant" in joined:
        caveats.append(
            "The sequential penalty applied to every team configuration in "
            "the sweep, including centralized orchestrator-worker."
        )
    return Message(kind="caveats", sender="skeptic", body={"caveats": caveats})


def citation_scout(msg: Message) -> Message:
    if msg.kind != "packet":
        raise ValueError(f"citation_scout rejected {msg.kind}")
    packet = msg.body
    citations, holes = [], []
    wanted = [
        ("90.2", "anthropic-2025-06"),
        ("15x", "anthropic-2025-06"),
        ("80.9", "deepmind-mit-2026-01"),
        ("17.2", "deepmind-mit-2026-01"),
        ("Flappy Bird", None),
    ]
    blob = {src["id"]: src["text"] for src in packet["sources"]}
    all_text = " ".join(blob.values())
    for needle, src_id in wanted:
        if needle in all_text and src_id:
            citations.append(f"{needle} <- {src_id}")
        else:
            holes.append(f"ungrounded or missing from packet: {needle}")
    return Message(
        kind="citations",
        sender="citation_scout",
        body={"citations": citations, "holes": holes},
    )


def synthesizer(claims_msg, caveats_msg, cites_msg) -> Brief:
    for m, kind in (
        (claims_msg, "claims"),
        (caveats_msg, "caveats"),
        (cites_msg, "citations"),
    ):
        if m.kind != kind:
            raise ValueError(f"synthesizer expected {kind}, got {m.kind} from {m.sender}")
    return Brief(
        title="Multi-agent research systems, sourced brief",
        claims=list(claims_msg.body["claims"]),
        caveats=list(caveats_msg.body["caveats"]),
        holes=list(cites_msg.body["holes"]),
        citations=list(cites_msg.body["citations"]),
    )


def run_message_graph(packet: dict) -> Brief:
    outbound = Message(kind="packet", sender="orchestrator", body=packet)
    c = claim_miner(outbound)
    s = skeptic(outbound)
    t = citation_scout(outbound)
    return synthesizer(c, s, t)


def run_shared_dict_bug(packet: dict) -> dict:
    state = {"notes": "", "packet": packet}

    def worker_a():
        state["notes"] = "A: extracted claims from three sources."

    def worker_b():
        state["notes"] = "B: listed caveats. (A's notes are gone.)"

    worker_a()
    worker_b()
    return state


def main() -> None:
    brief = run_message_graph(PACKET)
    print("=== message graph (workers cannot clobber each other) ===")
    print("title:", brief.title)
    print("claims:")
    for c in brief.claims:
        print(" -", c)
    print("caveats:")
    for c in brief.caveats:
        print(" -", c)
    print("citations:")
    for c in brief.citations:
        print(" -", c)
    print("holes:")
    for h in brief.holes:
        print(" -", h)
    lost = run_shared_dict_bug(PACKET)
    print("\n=== shared-dict anti-pattern (last write wins) ===")
    print("notes:", lost["notes"])


if __name__ == "__main__":
    main()
