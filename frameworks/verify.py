"""Assert every chapter port's run() matches, and build/invoke/kickoff execute.

No vendor packages. No network. From the repo root:

    python frameworks/verify.py
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

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
    """Run the framework entrypoints. Return extra failures."""
    fails = []
    built = mod.build()
    if built is None:
        fails.append(f"{port}: build() returned None")
        return fails
    if port == "adk":
        got = _normalize(built.run(None))
        if got != baseline:
            fails.append(f"{port}: build().run(None) != run()")
    elif port == "openai_agents":
        got = _normalize(mod.invoke())
        if got != baseline:
            fails.append(f"{port}: invoke() != run()")
    elif port == "anthropic_agents":
        got = _normalize(mod.invoke())
        if got != baseline:
            fails.append(f"{port}: invoke() != run()")
    elif port == "crewai":
        got = _normalize(built.kickoff())
        if got != baseline:
            fails.append(f"{port}: kickoff() != run()")
    elif port == "langgraph":
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
    print(f"OK {checked} ports across 14 chapters (run + build/invoke)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
