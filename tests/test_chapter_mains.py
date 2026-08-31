"""Run every chapter listing and framework port as a script under cp1252."""
from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK_SKIP = {"verify.py", "_rewire_live_sdks.py", "_fix_sys_path.py"}
FRAMEWORK_PORTS = {"adk.py", "openai_agents.py", "anthropic_agents.py", "langgraph.py", "crewai.py"}


def _sdks_installed() -> bool:
    """True when all five vendor packages import. Dotted names must not raise.

    ``find_spec('google.adk')`` imports the parent ``google`` package. On a
    stdlib-only install that is ``ModuleNotFoundError``, not ``None``.
    """
    for name in ("langgraph", "agents", "claude_agent_sdk", "crewai", "google.adk"):
        try:
            if importlib.util.find_spec(name) is None:
                return False
        except ModuleNotFoundError:
            return False
    return True


def _scripts() -> list[Path]:
    out: list[Path] = []
    sdks = _sdks_installed()
    for path in ROOT.rglob("*.py"):
        if "__pycache__" in path.parts or ".git" in path.parts:
            continue
        if path.name in FRAMEWORK_SKIP or path.name.startswith("_"):
            continue
        if "tests" in path.parts:
            continue
        if path.name in FRAMEWORK_PORTS and not sdks:
            continue
        text = path.read_text(encoding="utf-8")
        if 'if __name__ == "__main__"' in text:
            out.append(path)
    return sorted(out)


def test_every_main_exits_zero_on_cp1252(tmp_path: Path) -> None:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "cp1252"
    env["PYTHONUTF8"] = "0"
    env["CREWAI_TRACING_ENABLED"] = "false"
    env["CREWAI_DISABLE_TRACKING"] = "true"
    failed: list[str] = []
    for path in _scripts():
        proc = subprocess.run(
            [sys.executable, str(path)],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            encoding="cp1252",
            errors="replace",
            env=env,
            timeout=90,
        )
        if proc.returncode != 0:
            rel = path.relative_to(ROOT)
            failed.append(f"{rel}\n{proc.stderr or proc.stdout}")
    assert not failed, "mains failed under PYTHONIOENCODING=cp1252:\n\n" + "\n---\n".join(failed)


@pytest.mark.skipif(not _sdks_installed(), reason="pip install -r requirements-frameworks.txt")
def test_verify_ports() -> None:
    env = os.environ.copy()
    env["CREWAI_TRACING_ENABLED"] = "false"
    env["CREWAI_DISABLE_TRACKING"] = "true"
    proc = subprocess.run(
        [sys.executable, str(ROOT / "frameworks" / "verify.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=300,
        env=env,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "OK" in proc.stdout
