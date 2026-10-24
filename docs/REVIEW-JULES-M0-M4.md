# Jules M0–M4 ZIP review — 2026-10-24

**Status: UNACCEPTED PROTOTYPE.** Original Jules-exported Python sources and tests have been copied into this branch, without replacing `AGENTS.md`, historical theory files, or the existing development queue. Do not merge as a ready-to-install DSH plugin.

## Verified locally
- `PYTHONPATH=src python -m pytest -q`: **12 passed** (local fixtures only).
- Graph operations, activation propagation, edge decay, basic toy revision logic, and an in-process three-session example execute without exceptions.
- The ZIP contains no package installation metadata or working DSH host adapter.

## Reproduced critical gaps
1. **No persistence**: `DHSNeuroMemoryPlugin` (actual class: `DSHNeuroMemoryPlugin`) creates a fresh in-memory `EngramGraph` every time; another instance has zero previous memory nodes. No durable storage/restore.
2. **No self-built association graph**: ingesting two related messages yields two nodes and **zero edges**. The “multi-hop” end-to-end test explicitly adds its own `SynapticEdge` instead of testing relation formation from real conversation.
3. **Compression is lossy by truncation**: `compression.py` builds a string of turns and keeps only `chunk_text[:120]`, losing important information at the tail. `max_tokens` is ignored; token-savings estimate can claim a minimum of 10 regardless of actual savings.
4. **Duplicate IDs**: fast repeated compression and fast repeated revisions both generate the same second-based ID and overwrite nodes.
5. **Revision is overlap, not contradiction reasoning**: `find_conflicting_nodes` uses shared words/characters and `revise` adds inhibitory links and rewires positive edges without source/evidence/dependency semantics. Original statements can be incorrectly suppressed.
6. **Not a real DSH plugin yet**: `IDSHMemoryPlugin` is a new local Python ABC, not a verified extension from upstream. Official DSH is a Cordis/Node.js plugin runtime, while the referenced `dsh-fish-memory` ships `package.json`, `lib/index.js` and `cordis.patch.yml`. No JS/TS adapter, plugin manifest, bundle, install test or host hook validation is present.
7. **No fair baseline**: neither summary-only nor retrieval-only comparator, realistic indirect-cue dataset, restarts, multi-compaction benchmark, resource bound tests, nor measured superiority is present.

## Source references
- https://github.com/deepseek-ai/deepseek-harness
- https://github.com/Yuuyuko-uu/dsh-fish-memory
- Earlier research contract: `AGENTS.md`, `theory/INDEX.md`, `docs/DEVELOPMENT-QUEUE.md`.

## Suggested next milestones (do not silently declare M0–M4 complete)
1. **M0**: document/pin actual Cordis plugin interfaces from upstream code. Make a minimal installable JS/TS plugin shell or explicitly separate Python engine into an adapter process; test against a real DSH version.
2. **M1**: persistent event log/database, unique IDs, provenance and source-grounded automatic relation building. Test killed/restarted process and duplicate ingestion.
3. **M2**: bounded activation over actual automatically built relations, controlled query latency/memory, replayable indirect-cue fixtures.
4. **M3**: revision with provenance, independent evidence roots and historical preservation, explicit conflict/unknown distinction; no blind lexical contradiction.
5. **M4**: real host integration smoke test plus fair baseline vs summary-only and retrieval-only. Report actual measures and negative results.

This report is a static code review and focused local replay, not a comprehensive security audit. There is no evidence of production compatibility or demonstrated long-term memory gain yet.
