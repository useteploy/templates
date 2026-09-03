# Ollama — the local model runtime

The model server itself, with no UI attached. Run it on the machine with the
RAM or the GPU, then point clients at it: Open WebUI on another box
(`OLLAMA_BASE_URL`), editor plugins, agents, or anything speaking its API.
Deploy:

    teploy template install ollama --server <name>

After it is up, pull a model on the server:

    teploy exec <server> -- docker exec ollama ollama pull llama3.2

The API listens on the published port (11434). Keep it on your LAN or
tailnet — it has no authentication of its own.

## GPU

The image auto-detects NVIDIA GPUs when the host has the nvidia container
toolkit installed. CPU-only works for small quantized models (8GB+ RAM).

## Pairs with

Open WebUI (`open-webui` template) for the chat experience — either the
all-in-one tag on one box, or that template's `:main` image pointed at this
one for the split layout.
