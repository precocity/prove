# The PROVE Lifecycle

Ten steps, five phases, one bounded refinement loop. The runner
(`python .prove/runner`) tracks each artifact's position and enforces the
gates; the agent crew performs the work; the expert owns the binding gate.

```
PROPOSE          RUN              OBSERVE            VERIFY              ENABLE
1 discover   →   5 scan       →   6 expert verdicts  →  9 final audit  →  10 ship
2 draft          (production      7 refine in place
3 test            engine,         8 re-scan
4 spec review     bounded)        (loop ≤ k times)
```

## Phase P — Propose

**1. Discover** *(Discovery agent)* — Parse a source document (policy text,
data contract, guideline, spec) into a structured artifact intent. Check the
existing landscape for duplicates or overlaps. Survey the corpus (bounded) for
signal frequency to prioritize.

**2. Draft** *(Drafter agent)* — Emit the candidate artifact **into the
production repository**, in the production rule language, absent from the
activation allowlist. From this moment the artifact is inactive-but-runnable
(P1 + P2). If the intent can't be expressed in the current rule language, that
is a signal to extend the engine with a *generic* capability — never to
approximate the logic in a throwaway script.

**3. Test** *(Tester agent)* — Generate golden fixtures: synthetic input
documents plus expected-findings files, committed to the regression suite. Run
the suite; it must be green before proceeding.

**4. Spec review** *(Council)* — Advisory multi-model (or single-model,
multi-pass) review of the artifact intent and config. Verdict: GO / NO-GO /
REVISE. Catches specification incoherence cheaply, before expert time is
spent. Advisory only.

## Phase R — Run

**5. Scan** *(Evidence agent)* — Production-engine sweep over a bounded corpus
sample (default 5,000 documents). Compute the fire rate. Sample flagged
documents (default 50). Emit the expert review workbook in the frozen,
engine-verbatim format (P3). Record provenance: engine/config version, corpus
slice, seed.

## Phase O + V — Observe & Verify (the refinement loop, steps 6–8)

```
loop i in 1..k (default k = 3):
    expert records per-finding verdicts (TP / FP / Unclear + free-text fix idea)
    fp_rate = |FP| / |verdicts|          → recorded in pipeline state
    if fp_rate < τ (default 0.10):  CONVERGED → step 9
    Refiner converts FP feedback into artifact edits (exclusions, scoping)
    human gate approves each edit        → edits the production artifact (P4)
    regression suite re-run              → red halts everything
    Evidence agent re-scans              → fresh workbook
if not converged after k iterations: ESCALATE
```

Escalation is a signal, not a failure. It routes the artifact back to
discovery ("the source guideline is ambiguous — get clarification") or to
engine development ("this needs a new generic detection capability") — never to
threshold-fudging.

Expect criteria drift: experts refine their own reading of the guideline as
they see concrete findings. That is an argument for making re-scans cheap, not
for demanding complete criteria up front.

## Phase E — Enable

**9. Final audit** *(Council)* — Advisory code review of the final artifact
diff and its fixtures.

**10. Ship** *(Tracker + human)* — Work item advanced. Activation performed by
a **human** adding one entry to the activation allowlist (P5). Regression
suite re-run and green. The runner's `activate` command enforces the gates
(converged FP rate, green regression, explicit human confirmation, allowlist
verification) but never performs the edit itself.

## Rules of engagement (all steps)

1. **Regression first.** Before touching any artifact, run the regression
   suite. After changes, run it again. Red = stop.
2. **One artifact at a time.** Never modify two artifacts in one edit.
3. **Raw corpus only.** All evidence via the production parser over raw
   documents. Derived extracts are forbidden inputs.
4. **Bounded scans.** Respect the corpus caps in `prove.config.toml`.
5. **Expert gate before activation. No shortcuts.** Draft → evidence → expert
   verdicts → refine if needed → *then* activate.
6. **Track every artifact** in your work-item system from acceptance through
   activation or retirement.
