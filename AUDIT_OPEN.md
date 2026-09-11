# Open audit items

Unresolved findings for this repository from the ChatGPT-led audit series
(2026-09-09 through 2026-09-11, passes 1-5; register:
teploy-neutron-lullmail expanded audit). Every P0/P1 finding has been fixed
and verified; the P2/P3 tail below is what remains.

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
