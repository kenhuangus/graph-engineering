"""Assert every chapter port's run() matches, and live SDK build/invoke execute.

Requires: pip install -r requirements-frameworks.txt

    python frameworks/verify.py
"""
from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

os.environ.setdefault("CREWAI_TRACING_ENABLED", "false")
os.environ.setdefault("CREWAI_DISABLE_TRACKING", "true")

ROOT = Path(__file__).resolve().parents[1]
PORTS = ("adk", "openai_agents", "anthropic_agents", "langgraph", "crewai")


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _normalize(value):
    if hasattr(value, "__dataclass_fields__"):
        return {k: _normalize(getattr(value, k)) for k in value.__dataclass_fields__}
    if isinstance(value, dict):
        return {k: _normalize(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normalize(v) for v in value]
    if isinstance(value, set):
        return sorted(_normalize(v) for v in value)
    return value


def exercise(mod, port: str, baseline):
    """Run the live SDK entrypoints. Return extra failures."""
    from agents.agent import Agent as OpenAIAgent
    from claude_agent_sdk import ClaudeAgentOptions
    from crewai import Crew
    from google.adk import Workflow

    fails = []
    built = mod.build()
    if built is None:
        fails.append(f"{port}: build() returned None")
        return fails
    if port == "adk":
        if not isinstance(built, Workflow):
            fails.append(f"{port}: build() is {type(built).__name__}, not google.adk.Workflow")
        got = _normalize(mod.run_adk(built))
        if got != baseline:
            fails.append(f"{port}: run_adk(build()) != run()")
    elif port == "openai_agents":
        if not isinstance(built, OpenAIAgent):
            fails.append(f"{port}: build() is {type(built).__name__}, not agents.Agent")
        got = _normalize(mod.invoke())
        if got != baseline:
            fails.append(f"{port}: invoke() != run()")
    elif port == "anthropic_agents":
        if not isinstance(built, ClaudeAgentOptions):
            fails.append(f"{port}: build() is {type(built).__name__}, not ClaudeAgentOptions")
        got = _normalize(mod.invoke())
        if got != baseline:
            fails.append(f"{port}: invoke() != run()")
    elif port == "crewai":
        if not isinstance(built, Crew):
            fails.append(f"{port}: build() is {type(built).__name__}, not crewai.Crew")
        got = _normalize(mod.invoke())
        if got != baseline:
            fails.append(f"{port}: invoke() != run()")
    elif port == "langgraph":
        if not hasattr(built, "invoke"):
            fails.append(f"{port}: compile() did not return an invocable graph")
        walked = built.invoke({})
        if not isinstance(walked, dict):
            fails.append(f"{port}: compile().invoke({{}}) did not return a dict")
        elif "visited" in walked and not walked["visited"]:
            fails.append(f"{port}: invoke() visited no nodes")
    return fails


def main() -> int:
    sys.path.insert(0, str(ROOT / "frameworks"))
    failed: list[str] = []
    checked = 0
    for ch in [f"ch{i:02d}" for i in range(1, 15)]:
        sys.path.insert(0, str(ROOT / ch / "src"))
        first = None
        for port in PORTS:
            path = ROOT / ch / "frameworks" / f"{port}.py"
            if not path.is_file():
                failed.append(f"{ch}/{port}: missing file")
                continue
            mod = _load(path, f"{ch}_{port}")
            if not hasattr(mod, "run") or not hasattr(mod, "build"):
                failed.append(f"{ch}/{port}: missing run() or build()")
                continue
            got = _normalize(mod.run())
            if first is None:
                first = got
            elif got != first:
                failed.append(f"{ch}/{port}: run() != {PORTS[0]}")
            failed.extend(f"{ch}/{msg}" for msg in exercise(mod, port, got))
            checked += 1
        sys.path.pop(0)
    if failed:
        print("FAIL")
        for line in failed:
            print(" ", line)
        return 1
    print(f"OK {checked} live-SDK ports across 14 chapters (run + build/invoke)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
