# PROVE

**P**ropose → **R**un → **O**bserve → **V**erify → **E**nable

An agentic development framework for producing machine-executed business logic
faster — compliance rules, data-quality checks, detection heuristics, alert
conditions, and other deterministic artifacts — without sacrificing the
production safeguards that make the logic dependable.

## The problem it solves

Writing deterministic rules by hand is slow, repetitive, and difficult to
scale. Asking a stochastic agent to write them directly into production is
fast, but leaves too much of the process implicit: requirements, tests,
examples, expert decisions, and lessons from previous iterations disappear
into chat history.

PROVE turns that work into a repeatable production loop. Agents handle the
high-volume reasoning and drafting; deterministic commands run the real engine,
measure results, enforce gates, and preserve the artifacts that make the next
task faster. The project gradually accumulates its own domain vocabulary,
examples, exclusions, fixtures, and operating knowledge. Agents do not need to
"remember" a conversation to improve — the repository becomes the memory.

The core discipline is:

| Principle | Meaning |
|---|---|
| **P1 — Single implementation locus** | Candidate logic exists in exactly one place: your production repo, in your production rule language. Agents do not maintain a shadow implementation. |
| **P2 — Inactive-but-runnable staging** | The engine evaluates new artifacts before they are enabled, so agents can test and refine ideas without changing live decisions. |
| **P3 — Production-path evidence** | Examples, measurements, and diagnostics come from the real parser and production engine, not a throwaway approximation. |
| **P4 — Refine in place** | Feedback edits the production artifact itself; the next run measures the actual change. There is no slow porting step at the end. |
| **P5 — Data-only activation** | Shipping is a small, explicit activation change guarded by a green regression suite. |

The result is a faster feedback loop with an inspectable record of what was
proposed, tested, learned, changed, and shipped.

## What's in the box

- **An agent crew** (8 roles, rename to taste): Orchestrator, Discovery,
  Drafter, Evidence, Refiner, Council, Tester, Tracker. Personas are markdown
  files with fill-in-the-blank domain knowledge — your AI coding assistant
  plays every role.
- **A lifecycle** with a bounded, measurable refinement loop: candidate →
  fixtures → advisory review → corpus scan → findings → refine → re-scan →
  converge (or escalate) → audit → data-only activation.
- **Deterministic rails** enforced by a thin, stdlib-only Python runner:
  resumable pipeline state, gate checks, halt-on-red-regression, bounded
  iteration, activation ceremony. Agents propose; the rails dispose.
- **An onboarding interview**: after install, your AI assistant interviews you
  about your domain, engine, corpus, and expert workflow, then configures
  everything.

## Install

Run this from the root of the project you want to configure:

```bash
npx --yes prove-method install
```

`npx` downloads the public `prove-method` package temporarily and runs its
installer. Users do **not** clone this GitHub repository, install a global
package, or need access to the private source repository. They only need
Node.js 18+ and internet access to npm. The `--yes` flag accepts npx's prompt
to download the package; it is useful for scripts and can be omitted for an
interactive confirmation.

The installer asks which AI tools you use (GitHub Copilot, Claude Code, Cursor,
or generic `AGENTS.md`) and which agent roles you want. It then creates this
inside the current project:

```text
.prove/                 PROVE agents, docs, and Python runner
prove.config.toml       project-specific configuration template
.github/...             Copilot instructions, if selected
CLAUDE.md               Claude Code instructions, if selected
.cursor/...             Cursor rules, if selected
AGENTS.md               generic agent instructions, if selected
```

The installer does not modify your production logic or activate anything. It
only adds the PROVE scaffolding and tool instructions. It also preserves an
existing `prove.config.toml` and updates only its own marked instruction block
when run again.

After installation, open the project in your AI tool and say:

> Read `.prove/docs/ONBOARDING.md` and interview me to configure PROVE for
> this project.

The AI assistant will ask about your engine, artifact format, domain expert,
corpus, regression command, and activation allowlist. After onboarding, run:

```bash
python .prove/runner check
```

Python 3.11+ is needed for the runner and is not needed merely to install the
scaffolding.

For maintainers publishing a release from the private source checkout:

```bash
npm login
npm publish
```

The package name is `prove-method`. Publishing requires npm ownership of that
name; users only run the `npx` command above.

For local development without npm, run the installer directly:

```bash
node tools/install.js --dir /path/to/your/project
```

## Requirements

- Node.js 18+ (installer only)
- Python 3.11+ (runner)
- A production engine that can evaluate staged-but-inactive artifacts — or the
  willingness to add that affordance. It is the one architectural prerequisite
  (P2), and it is the retrofit worth prioritizing.

## Fit test

PROVE fits your task if you can name three things:

1. **An engine** — production code that executes declarative logic over
   documents/records (a rules engine, a dbt/SQL layer, a validation pipeline).
2. **A binding expert** — a human whose sign-off gates deployment.
3. **A corpus** — real documents the engine can be run over to generate
   evidence.

Works for: carrier compliance rules, medallion-architecture data-quality
checks, clinical alert rules, AML detection scenarios, content-moderation
policies, tax logic, and any repeatable logic production system. It is not a
fit for one-off analyses or tasks with no production engine.

## Daily loop

```bash
python .prove/runner status       # what's in flight, what's next — run first, every session
python .prove/runner regression   # your golden-fixture suite, before and after any change
python .prove/runner start MyNewRule
python .prove/runner advance MyNewRule
python .prove/runner record MyNewRule --fire-rate 0.012 --fp-rate 0.08
python .prove/runner activate MyNewRule   # gate-checked, human-confirmed, data-only
```

Your AI assistant (as the Orchestrator) drives these commands for you; the
runner exists so the gates are enforced in code, not in prompt text.

## Provenance

PROVE is a general-purpose version of an agentic production workflow developed
for authoring compliance rules. Its philosophy is simple: let agents propose
and reason quickly, give them deterministic production-grade tools, preserve
inspectable intermediate artifacts, and let humans make the decisions that
bind the result to production.

*Internal/private for now — no license granted.*
