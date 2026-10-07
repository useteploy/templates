# Open audit items

Unresolved findings for this repository from the ChatGPT-led audit series
(2026-09-09 through 2026-09-11, passes 1-5; register:
teploy-neutron-lullmail expanded audit). The status below describes that
historical register only; the 2026-10-06 addendum records newer findings and their current limits.

Open items: 0 fixed-in-part, 2 deferred (see annotations)

## Resolved from this register

- useteploy__templates-03 — fixed 2026-09-11:
  - `ci/validate.py` + `.github/workflows/validate.yml` (weekly +
    push/PR): structural catalog validation (unique names, every entry
    has a template, declared variables match `{{placeholders}}` actually
    used in both directions, listed accessories exist, sentinel shapes,
    orphaned template dirs), plus a render check that clones
    teploy-cli@main and runs its TestRenderAllCatalogTemplates — every
    template rendered with hostile YAML-unsafe values through the exact
    production path (substitution, secret generation) and parsed with the
    real Teploy config parser.
  - `docs/BACKUPS.md`: backup scope per stateful template (volumes,
    engine-aware db accessory dumps vs crash-consistent volume copies)
    and the pre-upgrade backup checklist.

## DEFERRED (decision)

- useteploy__templates-01 — digest-pinned image bundles. The current mix
  is deliberate and documented in the templates themselves: stateful
  cores are pinned with written rationale (teploy-ship's nucleus
  accessory "PINNED, not :latest — a storage engine is the last thing
  that should change underneath you unannounced. Bump deliberately";
  immich's postgres image pinned to its extension combination), while
  application images float (wordpress:latest, jellyfin:latest, ...) so
  operators get app updates without a catalog bump. Moving the whole
  catalog to immutable digests means taking on coordinated release
  tracking for every upstream app plus an upgrade-path story — a product
  decision, not a mechanical fix. Revisit alongside any catalog
  versioning work. (The acceptance test also needs clean deploy hosts
  and persisted-data fixtures this repo has no infrastructure for.)
- useteploy__templates-02 — typed catalog variable schema, in part. The
  behavioral substance landed with the teploy-cli fixes
  (useteploy__teploy-cli-01/-03, 2026-09-11): YAML-safe rendering that
  round-trips hostile password values (tested with quotes, colon-space,
  hash, newlines, true/number lookalikes), rejection of missing
  variables before deploy, and errors that name variables without ever
  printing supplied values. What remains is the index.json schema bump
  to typed variables ({"name","secret",...}): it must roll out
  CLI-first (older teploy binaries parse `variables` as a plain string
  list and would break on an object form), and no consumer uses the
  metadata yet — landing it now adds version-skew risk without
  behavior. Defer until an interactive install/prompting UX exists that
  will consume it.


## 2026-10-06 documentation corrections

Audited against templates `271c2970de5d80f062bdb105d99a97f4075dce00` and
teploy-cli `efd3b57eb571ce6e1e43e65bf91e8229d4b98e40`.

- TPL-02: corrected all 16 README domain arguments to `--domain`; the CLI's
  required flag is not satisfied by `--var domain=...`.
- TSEM-01/TSEM-02: corrected the shared-bridge trust boundary and removed
  the claim that ordinary UFW rules make Docker-published ingress
  Tailnet-only. Ship/Ollama now warn about the all-interface default and
  require explicit binding or a verified firewall boundary. This is a
  documentation fix, not per-app network isolation or a change to defaults.
- TSEM-04: documented positional accessory names, required bucket, explicit region,
  remote AWS prerequisites, retained/backup-only manifest handling after
  one-step install, and backup consistency/restore limits. Corrected
  Nucleus's generic-archive dispatch and several persistence descriptions.
- TSEM-05: replaced invalid Home Assistant app/restart syntax, made host
  selection explicit, and replaced blanket subnet trust/blind YAML append
  with a version-aware repair: secure loopback UI access for 2026.8+, and
  an inspected, backed-up YAML edit only for older releases. Current upstream
  HTTP settings are UI-managed; YAML is ignored after migration.
- TSEM-06: Ollama model pull now uses app exec with explicit app/host,
  allowing the CLI to select its versioned container.
- TSEM-07: documented current CPU-only template support; toolkit/image
  changes alone do not supply the GPU allocation the CLI cannot express.
- Related follow-on guidance: Lullmail logs now specify app/host after
  one-step install.

Validation: `ci/validate.py` covers all 20 catalog entries;
`ci/validate_docs.py` checks documentation commands and source contracts,
and can export the exact command fixtures for `ci/docs_cli_test.go` in the
real CLI package. CI runs the admission test plus the existing render test.
These checks do not execute command handlers or deploy/restore containers.
Do not claim local Go-test success without a working Go toolchain.

Still open (not silently closed by documentation): TPL-01 WordPress managed
persistence and existing-data migration; TPL-03 Lullmail URI password
encoding; TSEM-03 supplied secret/sentinel semantics; CLI-08 private
manifest output; CLI-09 server override persistence; other CLI recovery
and lifecycle defects in the upstream audit. No credential, image, port,
volume, ingress or other runtime manifest values were changed by this pass.
Live install/upgrade/backup/restore, network isolation and GPU acceptance
remain untested and require a disposable target with representative data.
