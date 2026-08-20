# Anti-Pattern Catalog

Each of these produces review/serving skew. Treat every one as a defect on
sight, whether or not a divergence has been observed yet. AI agents have a
strong prior toward the first two — the prohibition must be stated in agent
instructions verbatim, and the tool surface should make the undisciplined
action unavailable, not merely discouraged.

## The throwaway detector *(forbidden by P1)*

A script re-implements the artifact's matching logic "equivalently" for a
survey or demo. It diverges on text normalization, section scoping, exclusion
lists, header inheritance — the details a quick script never reproduces.

**Instead:** run the production engine in staged mode over a bounded corpus
sample (`evidence_command`).

## The notebook approval *(forbidden by P1 + P3)*

The expert reviews a notebook's dataframe filter over a cached extract. The
extract's schema froze months ago; the parser has moved on; scoping semantics
are absent.

**Instead:** the review workbook is emitted by the Evidence agent from live
engine findings, engine-verbatim.

## The prompt-only rule *(forbidden by P1)*

The "rule" exists as natural language in a prompt and an LLM adjudicates
samples for the expert. Non-deterministic, version-unpinnable,
un-regression-testable.

**Instead:** the LLM *drafts* the declarative artifact; the engine executes it.

## The port-after-approval *(forbidden by P4)*

Approved logic is re-keyed into the production system by a different person in
a different language. The canonical skew generator — the entire discipline
exists to delete this step.

**Instead:** the artifact was drafted in the production repo on day one; there
is nothing to port.

## The eager activation *(forbidden by P5 + the human gate)*

Artifact activated to "see how it does," with intent to review later. Inverts
the gate; unvetted findings reach users or auditors.

**Instead:** staged findings flow to the side channel — you can watch live
behavior at zero user exposure.

## The cleaned-up evidence *(forbidden by P3)*

Someone "improves" the engine output before showing the expert — rewording
messages, merging columns, summarizing findings. A rendering layer that can
skew.

**Instead:** frozen workbook schema, engine-verbatim evidence block. Add
context columns; never alter the finding itself.

## The two-rule edit *(forbidden by change isolation)*

One commit adjusts two artifacts "while I'm in there." Regression diffs become
unattributable; rollbacks take hostages.

## The unbounded sweep *(forbidden by corpus governance)*

A "quick" grep or scan over the full corpus with no file or time cap, holding
the pipeline (and your machine) hostage.

**Instead:** bounded survey tooling, fast enough that people actually use it.

## Prompt-layer skew *(the same disease, different layer)*

The same shared fact (corpus path, governance rule, schema) restated
independently in several agents' prompts, drifting apart over time.

**Instead:** shared facts live in exactly one place and are injected into
every agent context at composition time. In PROVE that place is
`prove.config.toml` + `.prove/docs/`.
