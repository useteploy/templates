# teploy-ship template

Issues in, verified pull requests out — the self-hosted coding agent.

`teploy template install teploy-ship --server <name> [--port 7460]`

## Status of this template

The template is complete and render-tested, but it deploys
`ghcr.io/useteploy/teploy-ship:stable`, which is **not published yet** — the
Ship repository is private and its first public release is pending. Until the
image exists, `install` fails at the pull step.

**Flip sequence (maintainers):** publish the image (`deploy/build-image.sh
--push` in the teploy-ship repo), add this entry to `index.json`, and
redeploy teploy-site (its /ship page copy is committed and waiting —
`teploy-site@3887f5d`):

```json
{
  "name": "teploy-ship",
  "description": "Self-hosted coding agent: issues in, verified pull requests out",
  "accessories": ["nucleus"],
  "variables": []
}
```

The template directory ships ahead of the index entry deliberately:
`teploy template info teploy-ship` works by direct fetch, so early adopters can
read the shape, while `teploy template list` shows nothing that cannot yet
install cleanly.

## After install

1. Save the three generated secrets printed once at install.
2. `teploy secret set` your worker credentials (git deploy token, model key,
   sandbox token) — see the comments in `teploy.yml`.
3. Open the dashboard at `http://<server>:7460` (token = `SHIP_WEB_TOKEN`).
4. Point it at repos: allowlist the origins, then per repo
   `teploy-ship evidence set <owner/repo> --test-command "..."` so PRs carry
   the suite result.
