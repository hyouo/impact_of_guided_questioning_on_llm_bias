# Reproduction registry

This directory is the canonical, machine-readable coverage map for the public
Transformer Circuits / Anthropic interpretability source catalog.

The map separates two questions that are often conflated:

1. **Coverage:** has this repository implemented any protocol for the source,
   and is that coverage complete or partial?
2. **Mode:** is the implementation an exact reproduction, an open-model
   analogue, a transparent proxy, or reference-only integration?

A transparent NumPy counterexample can be scientifically useful without being
a numerical reproduction of a Claude experiment. Likewise, reproducing a
directional effect on open weights does not recreate unpublished model
activations, feature dictionaries, training data, or replacement models.

Canonical files:

```text
reproductions/transformer_circuits_v1.json
schemas/reproduction-registry-v1.schema.json
sources/transformer_circuits_catalog.csv
```

The registry covers every catalog row exactly once. It stores current
protocols, exact-reproduction feasibility, blockers, target mode, compute
tier, acceptance criteria, and next implementation step.

Validate and inspect it with:

```bash
python scripts/validate_reproduction_map.py
llm-theory-lab validate-reproduction-map
llm-theory-lab reproduction-map --summary-only
llm-theory-lab reproduction-map --status planned --priority P0
```

A source can move to a stronger status only when the pull request includes:

- a pinned model or architecture revision;
- a fixed dataset or generator and hash;
- preregistered metrics, tolerances, controls, and falsifiers;
- raw and canonical results;
- an evidence-ledger record;
- deviations from the original public protocol;
- a clear statement of what remains unreproduced.

Do not edit the generated Markdown matrix by hand. After reviewing a registry
change, run:

```bash
python scripts/validate_reproduction_map.py --write-docs
```

Then commit the registry and generated document together.
