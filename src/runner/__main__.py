"""PROVE runner — deterministic rails for the artifact lifecycle.

Usage: python .prove/runner <command> [args]

Commands:
  init                        create state file, validate config
  check                       validate config, flag TBDs and bad paths
  status                      show all in-flight artifacts and next steps
  start <artifact>            register a new candidate artifact
  advance <artifact> [--to S] move to the next lifecycle step (gated)
  record <artifact> [--fire-rate X] [--fp-rate Y] [--note TEXT]
  regression                  run the configured golden-fixture suite
  activate <artifact>         guided, human-executed, data-only activation
"""
from __future__ import annotations

import argparse
import sys

import config
import lifecycle
import state as state_mod


def cmd_init(_args, cfg):
    st = state_mod.load()
    state_mod.save(st)
    print(f"state file ready: {config.STATE_PATH}")
    probs = config.problems(cfg)
    if probs:
        print(f"config has {len(probs)} open item(s) — run: python .prove/runner check")
    else:
        print("config is fully filled in.")


def cmd_check(_args, cfg):
    probs = config.problems(cfg)
    if not probs:
        print("config OK — no TBDs, all paths exist.")
        return
    print(f"{len(probs)} problem(s) in prove.config.toml:")
    for p in probs:
        print(f"  - {p}")
    sys.exit(1)


def cmd_status(_args, cfg):
    st = state_mod.load()
    arts = st["artifacts"]
    print(f"PROVE status — {cfg['project'].get('name', '?')}")
    if not arts:
        print("no artifacts in flight. Start one: python .prove/runner start <name>")
        return
    for name, a in arts.items():
        tag = "SHIPPED" if a.get("shipped") else a["step"]
        fp = f"fp={a['fp_rate']:.3f}" if a.get("fp_rate") is not None else "fp=?"
        fr = f"fire={a['fire_rate']}" if a.get("fire_rate") is not None else "fire=?"
        print(f"  {name}: [{tag}] iter={a['iteration']} {fr} {fp} (updated {a['updated']})")
        if not a.get("shipped"):
            if a["step"] == "ship":
                print("      next: python .prove/runner activate " + name)
            else:
                print(f"      next: advance to '{lifecycle.next_step(a['step'])}'")


def cmd_start(args, _cfg):
    st = state_mod.load()
    if args.artifact in st["artifacts"]:
        raise SystemExit(f"artifact '{args.artifact}' already exists")
    art = state_mod.new_artifact()
    state_mod.log(art, "registered at step 'discover'")
    st["artifacts"][args.artifact] = art
    state_mod.save(st)
    print(f"registered '{args.artifact}' at step 'discover'.")


def cmd_advance(args, cfg):
    st = state_mod.load()
    art = state_mod.get_artifact(st, args.artifact)
    target = args.to or lifecycle.next_step(art["step"])
    lifecycle.check_transition(art, target, cfg)
    prev = art["step"]
    lifecycle.apply_transition(art, target)
    state_mod.log(art, f"advanced {prev} -> {target}")
    state_mod.save(st)
    extra = f" (refinement iteration {art['iteration']})" if prev == "refine" and target == "scan" else ""
    print(f"'{args.artifact}': {prev} -> {target}{extra}")


def cmd_record(args, _cfg):
    st = state_mod.load()
    art = state_mod.get_artifact(st, args.artifact)
    parts = []
    if args.fire_rate is not None:
        art["fire_rate"] = args.fire_rate
        parts.append(f"fire_rate={args.fire_rate}")
    if args.fp_rate is not None:
        art["fp_rate"] = args.fp_rate
        parts.append(f"fp_rate={args.fp_rate}")
    if args.note:
        parts.append(args.note)
    if not parts:
        raise SystemExit("nothing to record — pass --fire-rate, --fp-rate, and/or --note")
    state_mod.log(art, "recorded: " + "; ".join(parts))
    state_mod.save(st)
    print(f"recorded on '{args.artifact}': " + "; ".join(parts))


def cmd_regression(_args, cfg):
    cmd = cfg["engine"]["regression_command"]
    if cmd in ("", "TBD"):
        raise SystemExit("[engine] regression_command is not configured")
    rc = lifecycle.run_command(cmd)
    print("regression: GREEN" if rc == 0 else f"regression: RED (exit {rc})")
    sys.exit(rc)


def cmd_activate(args, cfg):
    st = state_mod.load()
    art = state_mod.get_artifact(st, args.artifact)
    if art.get("shipped"):
        raise SystemExit(f"'{args.artifact}' is already shipped")
    if art["step"] != "ship":
        raise SystemExit(f"'{args.artifact}' is at '{art['step']}' — must reach 'ship' first")
    fp, thresh = art.get("fp_rate"), cfg["review"]["fp_threshold"]
    if fp is None or fp >= thresh:
        raise SystemExit(f"expert gate not satisfied: fp_rate={fp} (threshold {thresh})")

    print("pre-activation regression…")
    if lifecycle.run_command(cfg["engine"]["regression_command"]) != 0:
        raise SystemExit("regression RED — fix before activating")

    activation_file = cfg["engine"]["activation_file"]
    print(
        f"\nActivation is a HUMAN, data-only edit (P5). Add '{args.artifact}' to\n"
        f"  {activation_file}\n"
        "then press Enter here. (Ctrl-C to abort.)"
    )
    input()

    text = (config.ROOT / activation_file).read_text(encoding="utf-8")
    if args.artifact not in text:
        raise SystemExit(f"'{args.artifact}' not found in {activation_file} — activation NOT recorded")

    print("post-activation regression…")
    if lifecycle.run_command(cfg["engine"]["regression_command"]) != 0:
        raise SystemExit("post-activation regression RED — revert the activation edit and investigate")

    art["shipped"] = True
    state_mod.log(art, "SHIPPED: activated via data-only edit, regression green")
    state_mod.save(st)
    print(f"'{args.artifact}' is live. Close out the work item (Tracker).")


def main() -> None:
    p = argparse.ArgumentParser(prog="python .prove/runner", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init")
    sub.add_parser("check")
    sub.add_parser("status")
    sp = sub.add_parser("start"); sp.add_argument("artifact")
    sp = sub.add_parser("advance"); sp.add_argument("artifact"); sp.add_argument("--to")
    sp = sub.add_parser("record"); sp.add_argument("artifact")
    sp.add_argument("--fire-rate", type=float, dest="fire_rate")
    sp.add_argument("--fp-rate", type=float, dest="fp_rate")
    sp.add_argument("--note")
    sub.add_parser("regression")
    sp = sub.add_parser("activate"); sp.add_argument("artifact")

    args = p.parse_args()
    cfg = config.load()
    {
        "init": cmd_init, "check": cmd_check, "status": cmd_status,
        "start": cmd_start, "advance": cmd_advance, "record": cmd_record,
        "regression": cmd_regression, "activate": cmd_activate,
    }[args.cmd](args, cfg)


if __name__ == "__main__":
    main()
