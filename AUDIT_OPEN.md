# Open audit items

Unresolved findings for this repository from the ChatGPT-led audit series (2026-09-09 through 2026-09-11, passes 1-5; register: teploy-neutron-lullmail expanded audit). Every P0/P1 finding has been fixed and verified; the items below are the remaining P2/P3 tail plus one item needing validation. Fields are quoted from the audit register; line references point at the review commits listed per item where recorded.

Open items: 3 P2 (3 total)

## useteploy__templates-01 - P2 - Open improvement

**Release tested template/image bundles rather than resolving floating tags independently**

- Kind: Improvement
- Evidence: The sampled templates use adminer:latest, postgres:16 and Immich server/machine-learning :release tags, while the Immich database image is pinned to a particular extension/version combination.
- Impact: The same template revision can deploy different binaries over time, and independently updated server/ML/database components may not form the combination previously tested. This review did not establish a current compatibility failure.
- Proposed fix: Publish immutable, tested image digests or coordinated version sets, document an upgrade path, and update the bundle through smoke/compatibility tests rather than relying on moving tags.
- Acceptance test: Deploy the same template revision twice from clean hosts and verify identical image digests; test migration/rollback behavior on a copy of persisted data before approving a new bundle.
- Review commit: `d81aa8a0ccd6b9e6cdc6075674c3ee17e92face6` (last reviewed 2026-09-10)

## useteploy__templates-02 - P2 - Open improvement

**Give catalog variables a typed validation and secrecy contract**

- Kind: Improvement
- Evidence: index.json models variables as plain string lists such as domain and db_password. The sampled templates interpolate them into YAML, but the catalog contains no type, secret flag, generation policy or validation metadata. The deployment engine’s rendering and secret handling were not reviewed.
- Impact: Different consumers can prompt, validate, quote and persist the same variable differently; passwords should not be treated like ordinary display strings.
- Proposed fix: Define a versioned catalog schema with variable types, secret classification, required/default/generation behavior, and consistent YAML-safe rendering; verify each template against it.
- Acceptance test: Round-trip passwords containing quotes, colon, hash and newlines; validate domains, redact secret fields in logs/previews, and reject missing required variables.
- Review commit: `d81aa8a0ccd6b9e6cdc6075674c3ee17e92face6` (last reviewed 2026-09-10)

## useteploy__templates-03 - P2 - Open improvement

**Add repository-local template validation and documented data recovery checks**

- Kind: Improvement
- Evidence: The root inventory has no repository-local CI workflow or root validation harness. The sampled templates create persistent database/upload volumes, but their YAML does not define a recovery verification contract. External testing/operations may exist and were not inspected.
- Impact: Catalog drift or invalid rendered deployments can ship without a visible local gate; persistent volumes alone do not prove that application data can be restored consistently.
- Proposed fix: Add schema/rendering checks for every catalog entry and scheduled smoke tests for representative templates. Document backup scope, coordinated database/media restore and required pre-upgrade backup checks per stateful application.
- Acceptance test: Render every template with safe test inputs, validate it with the actual Teploy parser, and restore an Immich/Postgres fixture into a fresh deployment with record/file consistency checks.
- Review commit: `d81aa8a0ccd6b9e6cdc6075674c3ee17e92face6` (last reviewed 2026-09-10)

