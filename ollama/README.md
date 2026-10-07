# Ollama — the local model runtime

The model server itself, with no UI attached. Run it on the machine with the
RAM, then point clients at it: Open WebUI on another box
(`OLLAMA_BASE_URL`), editor plugins, agents, or anything speaking its API.
Deploy:

    teploy template install ollama --server <name>

After it is up, pull a model on the server:

    teploy app exec --app ollama --host <name> -- ollama pull llama3.2

Use the same server name as at install. Teploy resolves the running
versioned container; the bare `ollama` network alias is not a Docker
container name.

## Network access

The API has no authentication. The unchanged template publishes port 11434
on all host interfaces (`0.0.0.0`), even on a host that also has Tailscale.
Do not use one-step install on an Internet-reachable host without a tested
network restriction. Ordinary UFW rules do not reliably restrict
Docker-published ports; see [Docker's firewall
notes](https://docs.docker.com/engine/network/packet-filtering-firewalls/#docker-and-ufw).

For a new deployment, render and retain a manifest in a new private working
directory, set `server:` and an explicit `bind:` to the intended host
loopback or Tailnet IP, then deploy that manifest. There is no template
`--bind` flag. For an existing installation, edit its retained configuration
rather than blindly re-rendering it. Confirm access from an allowed client
and denial from an outside client before relying on the boundary. Binding
host ingress does not isolate peers on the shared `teploy` Docker bridge.

## GPU

This template uses the CPU path with the current Teploy CLI. Installing the
NVIDIA Container Toolkit alone does not allocate a GPU: the CLI has no GPU
request field and does not pass Docker's `--gpus` option. See [Ollama's
Docker instructions](https://docs.ollama.com/docker) for the separate runtime
and device-allocation requirements. GPU deployment requires a supported
runtime outside this template or a future, tested CLI GPU feature. CPU-only
can run small quantized models; size RAM for the model and context length.

## Pairs with

Open WebUI (`open-webui` template) for the chat experience — either the
all-in-one tag on one box, or that template's `:main` image pointed at this
one for the split layout.
