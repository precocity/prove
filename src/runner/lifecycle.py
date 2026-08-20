"""Lifecycle steps and gate enforcement for the PROVE runner.

The rails live here: step ordering, the refinement-loop bound, and the
convergence gate. Stochastic components propose; this module disposes.
"""
from __future__ import annotations

import subprocess

from config import ROOT

STEPS = ["discover", "draft", "test", "spec_review", "scan", "refine", "final_audit", "ship"]


def run_command(cmd: str) -> int:
    """Run a configured shell command from the project root; stream output."""
    print(f"$ {cmd}")
    return subprocess.run(cmd, shell=True, cwd=ROOT).returncode


def next_step(current: str) -> str:
    i = STEPS.index(current)
    if i == len(STEPS) - 1:
        raise SystemExit("artifact is already at 'ship' — use: activate")
    return STEPS[i + 1]


def check_transition(art: dict, target: str, cfg: dict) -> None:
    """Raise SystemExit if the transition violates a gate."""
    current = art["step"]
    if target not in STEPS:
        raise SystemExit(f"unknown step '{target}' (steps: {', '.join(STEPS)})")

    # The refine -> scan loop is the only allowed backward move.
    if STEPS.index(target) <= STEPS.index(current):
        if not (current == "refine" and target == "scan"):
            raise SystemExit(f"cannot move backward from '{current}' to '{target}'")

    if current == "refine" and target == "scan":
        max_iter = cfg["review"]["max_refine_iterations"]
        if art["iteration"] >= max_iter:
            raise SystemExit(
                f"refinement bound hit ({art['iteration']}/{max_iter} iterations).\n"
                "ESCALATE: route back to Discovery (ambiguous guidance) or Drafter\n"
                "(engine capability gap). Do not fudge the threshold."
            )
        return

    if STEPS.index(target) - STEPS.index(current) > 1:
        raise SystemExit(f"cannot skip steps: '{current}' -> '{target}'")

    if target == "refine" and art.get("fire_rate") is None:
        raise SystemExit("no fire_rate recorded for the scan — run: record <artifact> --fire-rate X")

    if target == "final_audit":
        fp = art.get("fp_rate")
        thresh = cfg["review"]["fp_threshold"]
        if fp is None:
            raise SystemExit("no fp_rate recorded — run: record <artifact> --fp-rate Y")
        if fp >= thresh:
            raise SystemExit(
                f"convergence gate: fp_rate {fp:.3f} >= threshold {thresh:.3f}.\n"
                "Loop back (advance --to scan after refining) or escalate."
            )


def apply_transition(art: dict, target: str) -> None:
    if art["step"] == "refine" and target == "scan":
        art["iteration"] += 1
    art["step"] = target
