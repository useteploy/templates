# teploy-ship template

Issues in, verified pull requests out — the self-hosted coding agent.

`teploy template install teploy-ship --server <name> [--port 7460]`

## Image

Deploys `ghcr.io/useteploy/teploy-ship:stable` (public; `stable` tracks the
latest published release, v0.2.0 at the time of writing). Needs teploy CLI
v0.1.29 or later — earlier versions leave the Nucleus data directory
root-owned on first start and the accessory crash-loops.

## After install

1. Save the three generated secrets printed once at install.
2. `teploy secret set` your worker credentials (git deploy token, model key,
   sandbox token) — see the comments in `teploy.yml`.
3. Open the dashboard at `http://<server>:7460` (token = `SHIP_WEB_TOKEN`).
4. Point it at repos: allowlist the origins, then per repo
   `teploy-ship evidence set <owner/repo> --test-command "..."` so PRs carry
   the suite result.
