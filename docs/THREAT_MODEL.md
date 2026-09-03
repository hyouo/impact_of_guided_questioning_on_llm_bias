# Threat Model

## 1. Purpose

This document identifies security and integrity risks for the repository, experiment runner, model backends, data, and published conclusions. It complements the repository [security policy](https://github.com/hyouo/impact_of_guided_questioning_on_llm_bias/blob/main/SECURITY.md), which describes private vulnerability reporting.

The project is a research and education platform, not a hardened multi-tenant inference service. Controls should be interpreted against that scope.

## 2. Assets

Assets requiring protection include:

- contributor and maintainer credentials;
- GitHub Actions permissions and release integrity;
- source code and dependency provenance;
- experiment definitions, thresholds, and result schemas;
- model and tokenizer revision provenance;
- prompt datasets, private inputs, and local caches;
- raw measurements and evidence records;
- the distinction between source findings, repository synthesis, and hypotheses;
- public safety boundaries that prevent research artifacts from becoming reusable attack material.

## 3. Trust boundaries

```text
GitHub contributor input
        ↓ review and CI
version-controlled repository
        ↓ package installation
local Python environment
        ↓ optional model loader
external model/dataset provider or local cache
        ↓ experiment execution
raw results and reports
        ↓ interpretation and release
public scientific claims
```

Each arrow crosses a different trust boundary. A valid Git commit does not imply that a model repository, dataset, generated report, or scientific interpretation is trustworthy.

## 4. Adversaries and failure sources

The model includes deliberate and accidental risks:

- a malicious contributor introducing code, workflow, dependency, or result manipulation;
- a compromised dependency, GitHub Action, model repository, or dataset;
- unsafe model loading that executes remote code;
- accidental credential or private-data publication;
- prompt or data content influencing an evaluator as if it were trusted control text;
- selective reporting, metric changes after inspection, or deletion of falsifying runs;
- incorrect attribution of a primary-source claim;
- a reader converting a safety mechanism example into an operational bypass technique;
- ordinary implementation mistakes, nondeterminism, version drift, and numerical instability.

## 5. Security goals

The repository aims to provide:

1. reviewable changes through pull requests and CODEOWNERS;
2. least-privilege automation;
3. dependency and static security analysis;
4. reproducible package and release artifacts;
5. explicit model, data, code, and configuration provenance;
6. separation of raw measurements from interpretation;
7. retention of null, falsified, skipped, and failed results;
8. bounded, non-operational safety experiments;
9. private disclosure of vulnerabilities and sensitive research findings.

It does not promise isolation from hostile code once a user deliberately enables arbitrary remote model code or runs unreviewed external scripts.

## 6. Major threat classes

### 6.1 Supply-chain compromise

**Threats:** malicious dependency updates, mutable action tags, package-name confusion, compromised release credentials.

**Controls:** Dependabot, dependency review, CodeQL, minimal workflow permissions, package building from reviewed tags, checksums, clean-environment installation, and release documentation.

**Residual risk:** stable major action tags and package version ranges are not cryptographic pinning. High-assurance releases may pin action commit SHAs and archive a complete dependency lock or software bill of materials.

### 6.2 Untrusted model and dataset loading

**Threats:** remote code execution, unsafe pickle formats, mutable revisions, poisoned tokenizers, oversized artifacts, hidden licensing constraints.

**Controls:** prefer immutable revisions, `safetensors`, explicit cache paths, documented `trust_remote_code` decisions, isolated environments, and no default CI model downloads.

**Residual risk:** model frameworks and artifacts remain complex. A model should be treated as untrusted software-adjacent input, not merely numerical data.

### 6.3 Prompt and content injection

**Threats:** untrusted prompt, document, or tool content being interpreted as control instructions by a model-based evaluator or report generator.

**Controls:** keep program control in typed code and configuration; treat model text as data; avoid using an LLM as the sole evaluator; validate structured output; preserve raw responses; use deterministic metrics where possible.

**Residual risk:** any model-based judge can still be influenced by the content it evaluates. Its result is evidence from an instrument, not ground truth.

### 6.4 Result and provenance manipulation

**Threats:** changing thresholds after observing outcomes, dropping seeds, overwriting earlier runs, rendering a report inconsistent with raw data, or citing the wrong code/model revision.

**Controls:** registered decision rules, append-only run directories, content hashes, machine-readable manifests, deterministic report generation, CI tests, and changelog/release records.

**Residual risk:** maintainers can still make interpretive mistakes. Independent replication and public raw measurements remain important.

### 6.5 Secret and privacy exposure

**Threats:** committed `.env` files, API keys in logs, private prompts, personal data, proprietary model outputs, or sensitive cache paths.

**Controls:** `.gitignore`, pre-commit private-key detection, repository hygiene checks, artifact review, and data policy.

**Residual risk:** secret scanners cannot recognize every sensitive value. Contributors must inspect staged changes and generated reports.

### 6.6 Safety-research misuse

**Threats:** public experiments becoming a reusable jailbreak corpus, automated bypass optimizer, harmful instruction set, or exploit chain.

**Controls:** bounded proxy tasks, mechanism-level descriptions, no operational payloads, private disclosure for sensitive findings, and maintainer review.

**Residual risk:** even abstract findings may have dual use. Publication detail should be proportional to scientific value and incremental misuse risk.

## 7. Out of scope

Unless the repository later becomes a hosted service, the following are outside the current assurance boundary:

- multi-user authentication and authorization;
- sandboxing arbitrary contributed code;
- secure storage of production secrets;
- availability guarantees;
- protection against users who intentionally run untrusted models with remote code enabled;
- proof that a model's generated answer is safe, factual, or aligned.

## 8. Secure experiment checklist

```text
[ ] Record exact model and tokenizer revisions.
[ ] Review model card, license, and remote-code requirements.
[ ] Prefer isolated environments and non-executable weight formats.
[ ] Keep credentials out of prompts, logs, and reports.
[ ] Treat all model text and retrieved documents as untrusted data.
[ ] Define metrics and controls outside the model prompt.
[ ] Preserve raw measurements and all result statuses.
[ ] Review generated artifacts before publication.
[ ] Remove operationally reusable harmful content.
```

## 9. Reassessment triggers

Revisit this threat model when the project adds a hosted service, automatic model downloads in CI, remote-code-enabled models, third-party execution with secrets, large public safety datasets, networked agents, or organization-level governance.
