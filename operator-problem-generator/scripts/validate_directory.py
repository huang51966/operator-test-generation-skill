#!/usr/bin/env python3
"""Validate every operator problem directory below a root."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def problem_dirs(root: Path) -> list[Path]:
    return sorted(path.parent for path in root.rglob("problem.json"))


def run_command(args: list[str], cwd: Path) -> tuple[bool, str]:
    completed = subprocess.run(
        args,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return completed.returncode == 0, completed.stdout.strip()


def validate_one(skill_root: Path, problem_dir: Path) -> dict:
    problem_json = problem_dir / "problem.json"
    reference_py = problem_dir / "reference.py"
    result = {
        "problem_dir": str(problem_dir),
        "status": "passed",
        "failed_stage": None,
        "message": "",
    }

    if not reference_py.exists():
        result.update(
            status="failed",
            failed_stage="layout",
            message="reference.py not found",
        )
        return result

    ok, output = run_command(
        [sys.executable, str(skill_root / "scripts" / "validate_problem.py"), str(problem_json)],
        skill_root,
    )
    if not ok:
        result.update(status="failed", failed_stage="validate_problem", message=output)
        return result

    ok, output = run_command(
        [
            sys.executable,
            str(skill_root / "scripts" / "run_reference.py"),
            str(problem_json),
            str(reference_py),
        ],
        skill_root,
    )
    if not ok:
        result.update(status="failed", failed_stage="run_reference", message=output)
        return result

    result["message"] = output
    return result


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", help="Directory containing problem subdirectories")
    parser.add_argument("--report", help="Optional JSON report path")
    args = parser.parse_args(argv[1:])

    skill_root = Path(__file__).resolve().parents[1]
    root = Path(args.root).resolve()
    entries = [validate_one(skill_root, path) for path in problem_dirs(root)]
    passed = sum(1 for entry in entries if entry["status"] == "passed")
    failed = len(entries) - passed
    report = {"root": str(root), "passed": passed, "failed": failed, "results": entries}

    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if failed == 0 and entries else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
