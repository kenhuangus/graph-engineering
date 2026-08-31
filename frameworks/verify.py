"""Assert every chapter port's run() matches the stdlib module.

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
            if not hasattr(mod, "run"):
                failed.append(f"{ch}/{port}: no run()")
                continue
            got = _normalize(mod.run())
            if first is None:
                first = got
            elif got != first:
                failed.append(f"{ch}/{port}: run() != {PORTS[0]} ({got!r} vs {first!r})")
            checked += 1
        sys.path.pop(0)
    if failed:
        print("FAIL")
        for line in failed:
            print(" ", line)
        return 1
    print(f"OK {checked} ports across 14 chapters")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
