"""State store for the PROVE runner: .prove/state.json."""
from __future__ import annotations

import json
from datetime import datetime, timezone

from config import STATE_PATH


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load() -> dict:
    if not STATE_PATH.exists():
        return {"artifacts": {}}
    with open(STATE_PATH, encoding="utf-8") as f:
        return json.load(f)


def save(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_PATH.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
        f.write("\n")
    tmp.replace(STATE_PATH)


def get_artifact(state: dict, name: str) -> dict:
    try:
        return state["artifacts"][name]
    except KeyError:
        raise SystemExit(f"unknown artifact '{name}' — run: python .prove/runner start {name}")


def log(art: dict, message: str) -> None:
    art.setdefault("log", []).append({"at": _now(), "msg": message})
    art["updated"] = _now()


def new_artifact() -> dict:
    return {
        "step": "discover",
        "iteration": 0,
        "fire_rate": None,
        "fp_rate": None,
        "shipped": False,
        "created": _now(),
        "updated": _now(),
        "log": [],
    }
