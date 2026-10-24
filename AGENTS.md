# AGENTS.md — ECR-NeuroMemory development contract

This repository is a public archive of ECR theory manuscripts and, prospectively, a **DSH long-term memory mechanism experiment**. The ten original Markdown files in `theory/01-foundations/`, `theory/02-memory-mechanisms/`, and `theory/03-research-extensions/` are historical sources. **Do not edit, replace, summarize in place, or delete them.** Read `theory/INDEX.md` first and follow the relevant originals.

## Assignment and scope

Build a separately testable, eventually installable **DeepSeek Harness (DSH) plugin** that evaluates whether bounded associative activation and evidence-preserving memory history outperform summary-only and conventional retrieval baselines under controlled budgets. The immediate goal is **better long-term recall and correct revision**, not consciousness, simulated emotions, or the full ECR runtime.

Use verified upstream interfaces, pinned versions, and minimal adaptation, primarily reviewing:
- https://github.com/deepseek-ai/deepseek-harness
- https://github.com/Yuuyuko-uu/dsh-fish-memory
These are **references**, not proof of compatibility. Inspect their current licenses and versions before reusing source. Keep upstream attribution and license notices wherever needed.

## Scientific / engineering boundaries

1. Memory objects need stable IDs, provenance, temporal ordering, entity/relation links, and distinct statuses for observed fact, quotation, hypothesis, interpretation, and adopted belief. Do not turn a recollection into independent evidence.
2. The current input activates a bounded working set through multi-entry associative graph traversal, propagation, competition/inhibition and decay. The memory backend—not an LLM manually traversing a graph—chooses candidate memories. Use statistical/NLP components as justified; graph weights are hypotheses to test, not biological facts.
3. Historical beliefs must survive correction. Propagate retractions along documented dependencies while retaining independent support, old claims, original events, and counterevidence.
4. A generated association is still a hypothesis. Separate activation frequency, strength of conviction, and evidence provenance. No self-reinforcing quote-loop should manufacture supporting observations.
5. Avoid hardcoded scenario answers, hidden answer keys, and changes to test data after observing results. No victory claims based only on fluent responses, retrieval hits or tests that don't exercise the production path.
6. Compare against **summary-only** and **retrieval-only** baselines with the **same language model, input history, prompt budget, and evaluation criteria**. Include indirect cues, conflicting revisions, multiple sessions / compactions, and adversarial distractions.
7. Keep experiments self-contained, testable offline with fixtures, and deterministic where possible. Do not require user API keys for the local smoke test. Publish reproducible commands and limitations.
8. Do not modify external accounts, deploy services, publish packages, or merge into the default branch without explicit authorization. Use a dedicated development branch and pull requests.

## Operating procedure for an autonomous coding agent

Start with `docs/DEVELOPMENT-QUEUE.md`. Find the **first unfinished, unblocked milestone**, implement one verifiable vertical slice end-to-end, run its acceptance checks, and record what passed/failed. Prefer small complete increments over mass refactors. Do not ask the user to select libraries, schema, or routine technical approaches: choose and justify them.

Create/update `docs/IMPLEMENTATION-STATUS.md` in your branch with:
- current milestone and latest commit;
- exact commands run with pass/fail evidence;
- feature gaps, compatibility/version assumptions, and blockers;
- **one next smallest useful step**.

If running on a recurring schedule, read the status and queue at the start of **each** run; do not assume private chat memory. Do not claim persistence between runs unless changes were committed and are available to the next run. Open a PR for a completed milestone; do not mark a milestone complete when code remains only in an unsubmitted scratch VM.

Stop rather than fabricate results if the required upstream dependency or environment is unavailable. Report the exact blocker and the independent parts that were verified. Avoid unbounded self-retry, uncontrolled API use, and expanding scope to unrelated ECR theories. A long-running agent may ask for required account authorization or final merge; it should not require daily product-direction decisions.
