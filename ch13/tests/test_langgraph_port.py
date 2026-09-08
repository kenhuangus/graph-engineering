"""Grader for the ch13 LangGraph port: the walk must come from the runtime.

Skips when langgraph is not installed, so the default stdlib-only run is
untouched; the frameworks CI job, which installs the SDKs, executes it.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

pytest.importorskip("langgraph")

_PORT = Path(__file__).resolve().parents[1] / "frameworks" / "langgraph.py"


def _load_port():
    spec = importlib.util.spec_from_file_location("ch13_langgraph_port", _PORT)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["ch13_langgraph_port"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_run_matches_the_other_ports():
    assert _load_port().run() == {
        "good": [],
        "bad": ["join_incomplete", "unconstrained_spend"],
    }


def test_good_walk_is_runtime_derived_and_legal():
    mod = _load_port()
    walk = mod.runtime_walk(mod.build())
    # The fan-out order is the scheduler's to choose; the join must hold.
    assert sorted(walk[:2]) == ["docs", "web"]
    assert walk[2:] == ["write", "human", "apply", "halt"]


def test_state_carries_no_trace_key():
    # The regression this port used to have: nodes appending their own
    # names to a state key, which any node could forge. The record must
    # come from the runtime, so state must not hold one.
    mod = _load_port()
    assert list(mod.State.__annotations__) == ["notes"]
