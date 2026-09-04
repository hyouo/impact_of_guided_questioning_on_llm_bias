# Evidence baselines

This directory contains reviewed, normalized evidence baselines used by CI.

- `baseline-v1/C01.json` through `C12.json` are reviewable per-experiment baselines derived from the successful `9df9a5c` main-branch CI artifact and normalized by the current claim registry.
- The same baseline and ledger schema are packaged under `llm_theory_lab.data`; repository checks require byte-identical copies.
- A baseline is updated only after reviewing why metrics or checks changed.
- Raw run bundles belong in `reports/` or release artifacts, not in Git history.
- Failed, inconclusive, skipped, and error records remain visible in run ledgers; a baseline is not a leaderboard of green checks.

Run:

```bash
python scripts/check_evidence_baseline.py
```

Schema and field semantics are documented in `docs/experiments/EVIDENCE_LEDGER.md`.
