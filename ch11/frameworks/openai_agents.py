"""Chapter 11 — Security, Identity, and Governance — OpenAI Agents SDK port.

Default-deny invoke, bound resume, cut-vertex reachability.

Guardrail / tool gate. A stranger does not get a handoff to spend.

Live: `pip install openai-agents` then
`from agents import Agent, Runner, handoff`.
This file imports agents.Agent / Runner. A local Model subclass drives the tool loop; no OpenAI key.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_HERE = Path(__file__).resolve().parent
sys.path[:] = [p for p in sys.path if Path(p).resolve() != _HERE]
sys.path.insert(0, str(_ROOT / "ch11" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from authz_graph import AuthzGraph, Principal
from agents import Agent, Runner, handoff
from runtime import homework_openai_agent, run_openai


def build():
    _ = (Agent, Runner, handoff)
    return homework_openai_agent(
        name="ch11_agent",
        instructions="Default-deny invoke, bound resume, cut-vertex reachability.",
        fn=run,
    )


def run():
    g = AuthzGraph(
        nodes=("start", "gate", "spend", "halt", "public"),
        edges=(("start", "gate"), ("gate", "spend"), ("spend", "halt"), ("start", "public"), ("public", "halt")),
        principals=(Principal("ken", "human"), Principal("stranger", "human")),
    )
    g.allow_invoke("ken", "spend")
    g.bind_resume("ken", "t1", "hash-a")
    return {
        "ken": g.can_invoke("ken", "spend"),
        "stranger": g.can_invoke("stranger", "spend"),
        "bad_resume": g.may_resume("ken", "t1", "hash-b"),
        "cut": g.is_cut_vertex("start", "spend", "gate"),
    }


def invoke(payload=None):
    return run_openai(build(), payload)


if __name__ == "__main__":
    print(invoke())
