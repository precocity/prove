# PROVE Onboarding — Interview Protocol

**Audience: the AI coding assistant.** When the user asks you to "set up
PROVE," "start PROVE onboarding," or similar, follow this protocol. You are
acting as the Orchestrator (see `.prove/agents/orchestrator.md`).

Your job: interview the user, then (a) fill in `prove.config.toml`, (b) fill
in every `> FILL-IN` block in `.prove/agents/*.md`, (c) validate the setup
with `python .prove/runner check`, and (d) tell the user what's still missing.

Ask questions **in small batches (2–4 at a time)**, adapt follow-ups to the
answers, and confirm your understanding by restating it before writing files.
If the user doesn't know an answer, record `TBD` and list it in the final
gap report — do not invent domain facts.

## Round 1 — The task and the fit test

1. **What are you building?** What kind of logic artifact does this project
   ship? (compliance rules, data-quality checks on bronze/silver/gold tables,
   alert conditions, moderation policies…)
2. **The engine.** What production code executes that logic today? Where does
   it live in this repo? What language/format are the artifacts (JSON config,
   SQL, YAML, Python classes)?
3. **The expert.** Who signs off before logic ships? What do they like to
   review in (spreadsheet, shared sheet, PR, dashboard)?
4. **The corpus.** What real documents/records can the engine be run over to
   generate evidence? Where, how many, any access constraints?

If the user cannot name an engine, an expert, and a corpus, PROVE is the wrong
tool — say so plainly and stop.

## Round 2 — The P2 audit (inactive-but-runnable)

5. Can your engine evaluate an artifact that is staged but **not** active —
   emitting findings somewhere without affecting production decisions?
   - If **yes**: what controls activation (allowlist file, flag column,
     toggle)? Where do staged findings go?
   - If **no**: this is the prerequisite retrofit. Help the user design it:
     an activation allowlist read at load time + a side channel in the
     output. Offer to implement it before continuing. Do not proceed to
     configure the lifecycle around an engine that cannot stage.

## Round 3 — Commands and rails

6. **Regression.** Is there a golden-fixture suite (known inputs + expected
   findings)? What command runs it? If none exists, plan its creation as the
   first Tester task.
7. **Evidence.** What command runs the engine over a corpus sample for one
   artifact? If none exists, plan it: it must use the production parser and
   engine, accept an artifact name, and respect a file cap.
8. **Bounds and thresholds.** Corpus scan cap (default 5000), review sample
   size (default 50), FP convergence threshold (default 0.10), max refinement
   iterations (default 3). Accept defaults unless the user objects.
9. **Tracking.** Work-item system (Azure DevOps, Jira, GitHub Issues, none)?
   Any rules about when tickets are created?

## Round 4 — Crew selection and domain knowledge

10. **Which agents does this project need?** Default: all eight. Trim if
    warranted (no ticket system → drop Tracker; no multi-model access →
    Council runs as a single-model multi-pass critic).
11. For each retained agent, gather the domain knowledge its `FILL-IN` blocks
    ask for (see the blocks themselves — e.g. Discovery needs source-document
    locations; Evidence needs the workbook column schema and delivery channel;
    Refiner needs the edit vocabulary the artifact format supports).
12. **Naming.** Offer to rename the agents to a theme of the user's choice.
    Names are cosmetic; roles are structural.

## Writing phase

- Fill `prove.config.toml` (root of the project). Every empty string you
  cannot fill becomes `"TBD"` — the runner's `check` command will flag them.
- Replace each `> FILL-IN (onboarding): …` block in `.prove/agents/*.md` with
  the gathered facts. Keep the blocks' headings so future re-onboarding can
  find them.
- Run `python .prove/runner init` then `python .prove/runner check`; fix what
  it flags.
- Produce a short **gap report**: what is configured, what is TBD, and the
  single next action (usually: create the regression suite, or implement the
  P2 retrofit, or run the first Discovery pass).

## Standing orders after onboarding

- Start every session with `python .prove/runner status`.
- Enforce the principles in `.prove/docs/PRINCIPLES.md` and refuse actions in
  `.prove/docs/ANTI-PATTERNS.md` — including your own impulse to write a
  quick standalone detector.
- When the user's request maps to a lifecycle step, adopt the matching agent
  persona from `.prove/agents/` and follow its instructions.
