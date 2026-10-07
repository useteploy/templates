# teploy-ship template

Issues in, verified pull requests out — the self-hosted coding agent.

Before installing, establish the network boundary described below. Then:

    teploy template install teploy-ship --server <name> --port 7460

## Image

Deploys `ghcr.io/useteploy/teploy-ship:stable` (public; `stable` tracks the
latest published release, v0.2.0 at the time of writing). Needs teploy CLI
v0.1.29 or later — earlier versions leave the Nucleus data directory
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

Nucleus has no published host port, but it has no authentication and shares
the shared `teploy` Docker bridge with every other Teploy app/accessory.
Only put mutually trusted workloads on this host. An ingress bind or firewall does
not create per-app Docker isolation.

## After install

1. Save the three generated secrets printed once at install.
2. `teploy secret set` your worker credentials (git deploy token, model key,
   sandbox token) — see the comments in `teploy.yml`.
3. Open the dashboard at `http://<server>:7460` (token = `SHIP_WEB_TOKEN`).
4. Point it at repos: allowlist the origins, then per repo
   `teploy-ship evidence set <owner/repo> --test-command "..."` so PRs carry
   the suite result.
