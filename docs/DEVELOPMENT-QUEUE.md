# ECR-NeuroMemory — executable milestone queue

**Purpose:** Small, autonomous, verifiable development increments. This is a proposed implementation backlog, not an amendment to the frozen ECR theories. Read [../AGENTS.md](../AGENTS.md) and [../theory/INDEX.md](../theory/INDEX.md).

## M0 — Reuse and compatibility audit
- [ ] Inspect current DSH plugin interfaces, compaction hooks, session/event persistence, and dsh-fish-memory implementation and license. Pin upstream versions or commit references.
- [ ] Establish minimal JS/TS (or equivalent) project scaffold, unit test runner, local repeatable fixtures, and CI check.
- [ ] Verify whether this host version supports all required event hooks. Clearly document unsupported integration points.
- **Accept when:** a clean checkout runs tests; real extension points and upstream versions are documented with file paths, not guessed.

## M1 — Durable event and relation memory
- [ ] Persist source events with stable IDs, exact source references, speaker/entity ownership, timestamps/order, and record type (observed/quoted/hypothetical/adopted/derived).
- [ ] Model multi-entry associations and belief-to-evidence dependencies. Distinguish associative edges from logical support.
- [ ] Support idempotent re-ingestion, restart/reload, simple import from upstream archive if feasible without losing source provenance.
- **Accept when:** restart tests prove events and relations survive; quoted beliefs do not automatically become facts; repeated ingestion doesn't duplicate evidence.

## M2 — Bounded activation engine and baselines
- [ ] Implement activation from current stimulus into related memories, bounded propagation and selection, transparent working-set diagnostics.
- [ ] Bound depth, fan-out, CPU/memory/time and prompt tokens. Handle memory scarcity and irrelevant noise.
- [ ] Implement two fair baselines: summary-only and ordinary direct retrieval, with identical query/task budgets.
- **Accept when:** blind fixtures demonstrate multi-hop and indirect-cue recall behavior; diagnostics show selected entry points, path, cutoff and provenance.

## M3 — Revisions and sustained-conversation benchmark
- [ ] Preserve old belief versions and conflicts; retract dependent conclusions on upstream withdrawal without destroying independently supported conclusions or original experiences.
- [ ] Create scripted conversations with resets/compaction, delays, vague cues, contradictory updates and distractors.
- [ ] Run fair accuracy, contradiction, retrieval-latency, storage size and token-cost comparisons. Record negative or equal results as prominently as positive results.
- **Accept when:** original/revised claims and support provenance are reconstructible; raw result data and benchmark commands can be independently rerun.

## M4 — DSH plugin adapter and packaging
- [ ] Adapt to an actual pinned DSH release after validating plugin extension points. Avoid editing DSH upstream or changing the historical theory files.
- [ ] Provide install, uninstall, import/export, reset/restore and error-recovery instructions and smoke tests.
- [ ] Include usage limits, unsupported host versions, risk notices and known failures.
- **Accept when:** a documented reproducible installation smoke test succeeds in the supported host version, or the implementation is explicitly labeled an **engine prototype only** if integration cannot be verified.

## Rules for future unattended runs

On **each** run: inspect this queue + `docs/IMPLEMENTATION-STATUS.md` if present; pick one unfinished milestone; do a testable increment; persist code and evidence to a branch/PR; update status in the *same branch*. Scheduled task runs may be isolated, so do **not** falsely assume they can see unmerged changes from a previous run. If the previous state is not accessible, stop and explain what must be merged or selected for continuity, rather than redoing work or claiming forward progress. Do not auto-merge to main.

No work on desktop pet UI, multi-agent orchestration, full personality simulator, autonomous inner monologue, or reproduction of the entire ECR research system in this project phase.
