"""Config loading and validation for the PROVE runner.

Stdlib only. Python 3.11+ (tomllib).
"""
from __future__ import annotations

import tomllib
from pathlib import Path

# Runner lives at <project_root>/.prove/runner/ — walk up to the root.
ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = ROOT / "prove.config.toml"
STATE_PATH = ROOT / ".prove" / "state.json"

REQUIRED = {
    "project": ["name", "domain"],
    "engine": ["regression_command", "evidence_command", "artifact_store", "activation_file"],
    "review": ["expert_channel", "fp_threshold", "max_refine_iterations", "sample_size"],
    "corpus": ["path", "scan_bound", "governance"],
    "tracking": ["system"],
}

PATH_FIELDS = [("engine", "artifact_store"), ("engine", "activation_file"), ("corpus", "path")]


def load() -> dict:
    if not CONFIG_PATH.exists():
        raise SystemExit(
            f"prove.config.toml not found at {CONFIG_PATH}.\n"
            "Run the installer, or copy the template from the PROVE repo."
        )
    with open(CONFIG_PATH, "rb") as f:
        return tomllib.load(f)


def problems(cfg: dict) -> list[str]:
    """Return a list of human-readable config problems (empty = healthy)."""
    out: list[str] = []
    for section, keys in REQUIRED.items():
        if section not in cfg:
            out.append(f"missing section [{section}]")
            continue
        for key in keys:
            val = cfg[section].get(key)
            if val is None:
                out.append(f"[{section}] {key} is missing")
            elif isinstance(val, str) and val.strip() in ("", "TBD"):
                out.append(f"[{section}] {key} is TBD — fill in during onboarding")
    for section, key in PATH_FIELDS:
        val = cfg.get(section, {}).get(key, "")
        if isinstance(val, str) and val and val != "TBD":
            if not (ROOT / val).exists():
                out.append(f"[{section}] {key} points to '{val}' which does not exist under {ROOT}")
    ev = cfg.get("engine", {}).get("evidence_command", "")
    if isinstance(ev, str) and ev not in ("", "TBD") and "{artifact}" not in ev:
        out.append("[engine] evidence_command has no {artifact} placeholder")
    return out
