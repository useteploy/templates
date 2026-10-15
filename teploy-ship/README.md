# teploy-ship template

Issues in, verified pull requests out — the self-hosted coding agent.

Before installing, establish the network boundary described below. Then:

    teploy template install teploy-ship --server <name> --port 7460

## Image

Deploys `ghcr.io/useteploy/teploy-ship:stable` (public; `stable` tracks the
latest published release, v0.2.0 at the time of writing). Needs teploy CLI
v0.1.29 or later — earlier versions leave accessory data directories
root-owned on first start and the accessory crash-loops.

## Network boundary

The default manifest publishes the dashboard on all host interfaces
(`0.0.0.0:7460`). A Tailscale installation or an ordinary UFW allow rule does
not make this Tailnet-only: [Docker-published traffic can bypass
UFW](https://docs.docker.com/engine/network/packet-filtering-firewalls/#docker-and-ufw).
Use a tested upstream/Docker-aware firewall boundary before one-step install.

For a new private deployment, render and retain a manifest in a new private
working directory, set `server:` and `bind:` to the intended host loopback
or Tailnet IP, then deploy that manifest. There is no template `--bind` flag.
Protect the rendered credentials with private file permissions and keep
them out of version control. For existing installations, edit the retained
configuration; do not re-render a secret-generating template as a repair.
Test access from both an allowed and a denied client.

The database is PostgreSQL 17 (the official pgvector build, pinned) with
password authentication, and it publishes no host port — it is reachable only
on the shared `teploy` Docker bridge, where presenting the install-time
`db_password` is required. It still shares that bridge with every other
Teploy app/accessory on the host, so deploy only mutually trusted workloads;
an ingress bind or firewall does not create per-app Docker isolation.

## After install

1. Save the three generated secrets printed once at install, and the
   `db_password` you supplied (it is the database credential for restores
   and manual `psql`).
2. `teploy secret set` your worker credentials (git deploy token, model key,
   sandbox token) — see the comments in `teploy.yml`.
3. Open the dashboard at `http://<server>:7460` (token = `SHIP_WEB_TOKEN`).
4. Point it at repos: allowlist the origins, then per repo
   `teploy-ship evidence set <owner/repo> --test-command "..."` so PRs carry
   the suite result.
