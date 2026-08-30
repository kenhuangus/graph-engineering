"""Chapter 6 — tiny in-memory runtime for three topologies.

Same job (classify, two research workers, write). Three patterns must
produce different traces. fanout_join runs both researchers before write
and the write sees both notes. supervisor_star never lets workers send
messages to each other — every hop goes through the supervisor.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Literal

Pattern = Literal["sequential_path", "supervisor_star", "fanout_join"]
WORKERS = frozenset({"classify", "research_web", "research_docs", "write"})


@dataclass
class Job:
    topic: str
    label: str = ""
    notes: dict[str, str] = field(default_factory=dict)
    document: str = ""


@dataclass(frozen=True)
class Message:
    src: str
    dst: str
    kind: str
    body: str = ""


@dataclass(frozen=True)
class TraceEvent:
    node: str
    superstep: int
    pattern: Pattern
    notes_snapshot: tuple[tuple[str, str], ...] = ()


@dataclass
class RunResult:
    pattern: Pattern
    job: Job
    trace: list[TraceEvent]
    messages: list[Message]


def _classify(job: Job) -> None:
    job.label = "needs_research" if job.topic else "empty"


def _research_web(job: Job) -> None:
    job.notes["web"] = f"web notes on {job.topic}"


def _research_docs(job: Job) -> None:
    job.notes["docs"] = f"docs notes on {job.topic}"


def _write(job: Job) -> None:
    web = job.notes.get("web", "")
    docs = job.notes.get("docs", "")
    job.document = f"# {job.topic}\n{web}\n{docs}"


def make_job(topic: str = "loops vs graphs") -> Job:
    return Job(topic=topic)


def sequential_path(job: Job) -> RunResult:
    """classify → research_web → research_docs → write. One node per superstep."""
    trace: list[TraceEvent] = []
    messages: list[Message] = []
    steps = [
        ("classify", _classify),
        ("research_web", _research_web),
        ("research_docs", _research_docs),
        ("write", _write),
    ]
    prev = "start"
    for i, (name, fn) in enumerate(steps):
        messages.append(Message(src=prev, dst=name, kind="handoff"))
        fn(job)
        trace.append(
            TraceEvent(
                node=name,
                superstep=i,
                pattern="sequential_path",
                notes_snapshot=tuple(sorted(job.notes.items())),
            )
        )
        prev = name
    messages.append(Message(src="write", dst="halt", kind="handoff"))
    return RunResult(pattern="sequential_path", job=job, trace=trace, messages=messages)


def supervisor_star(job: Job) -> RunResult:
    """Supervisor is the hub. Workers never message each other."""
    trace: list[TraceEvent] = []
    messages: list[Message] = []
    order = [
        ("classify", _classify),
        ("research_web", _research_web),
        ("research_docs", _research_docs),
        ("write", _write),
    ]
    superstep = 0
    for name, fn in order:
        messages.append(Message(src="supervisor", dst=name, kind="dispatch", body=job.topic))
        fn(job)
        trace.append(
            TraceEvent(
                node=name,
                superstep=superstep,
                pattern="supervisor_star",
                notes_snapshot=tuple(sorted(job.notes.items())),
            )
        )
        messages.append(
            Message(src=name, dst="supervisor", kind="report", body=job.label or job.document or str(job.notes))
        )
        superstep += 1
    messages.append(Message(src="supervisor", dst="halt", kind="halt"))
    return RunResult(pattern="supervisor_star", job=job, trace=trace, messages=messages)


def fanout_join(job: Job) -> RunResult:
    """classify, then both researchers in one superstep, then write.

    The join is real: write is not scheduled until both notes exist.
    """
    trace: list[TraceEvent] = []
    messages: list[Message] = []

    messages.append(Message(src="start", dst="classify", kind="handoff"))
    _classify(job)
    trace.append(TraceEvent(node="classify", superstep=0, pattern="fanout_join", notes_snapshot=()))

    # Fan-out: both researchers receive the classified job in the same superstep.
    messages.append(Message(src="classify", dst="research_web", kind="fanout"))
    messages.append(Message(src="classify", dst="research_docs", kind="fanout"))
    _research_web(job)
    _research_docs(job)
    # Record both as superstep 1, web first then docs (deterministic, still same step).
    snap = tuple(sorted(job.notes.items()))
    trace.append(TraceEvent(node="research_web", superstep=1, pattern="fanout_join", notes_snapshot=snap))
    trace.append(TraceEvent(node="research_docs", superstep=1, pattern="fanout_join", notes_snapshot=snap))

    if "web" not in job.notes or "docs" not in job.notes:
        raise RuntimeError("join incomplete: write requires both research notes")

    messages.append(Message(src="research_web", dst="write", kind="join"))
    messages.append(Message(src="research_docs", dst="write", kind="join"))
    _write(job)
    trace.append(
        TraceEvent(
            node="write",
            superstep=2,
            pattern="fanout_join",
            notes_snapshot=tuple(sorted(job.notes.items())),
        )
    )
    messages.append(Message(src="write", dst="halt", kind="handoff"))
    return RunResult(pattern="fanout_join", job=job, trace=trace, messages=messages)


def worker_to_worker_messages(result: RunResult) -> list[Message]:
    """Messages whose both endpoints are workers (illegal under supervisor_star)."""
    out: list[Message] = []
    for m in result.messages:
        if m.src in WORKERS and m.dst in WORKERS:
            out.append(m)
    return out
