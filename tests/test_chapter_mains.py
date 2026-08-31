"""Run every chapter listing and framework port as a script under cp1252."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _scripts() -> list[Path]:
    out: list[Path] = []
    for path in ROOT.rglob("*.py"):
        if "__pycache__" in path.parts or ".git" in path.parts:
            continue
        if path.name in {"verify.py"}:
            continue
        if "tests" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        if 'if __name__ == "__main__"' in text:
            out.append(path)
    return sorted(out)


def test_every_main_exits_zero_on_cp1252(tmp_path: Path) -> None:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "cp1252"
    env["PYTHONUTF8"] = "0"
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
            timeout=30,
        )
        if proc.returncode != 0:
            rel = path.relative_to(ROOT)
            failed.append(f"{rel}\n{proc.stderr or proc.stdout}")
    assert not failed, "mains failed under PYTHONIOENCODING=cp1252:\n\n" + "\n---\n".join(failed)


def test_verify_ports() -> None:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "frameworks" / "verify.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "OK" in proc.stdout
