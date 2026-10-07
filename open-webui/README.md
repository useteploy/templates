# Open WebUI — Local AI

ChatGPT-style chat, model library, and document RAG on your own server.
The `:ollama` image bundles Ollama, so local models work out of the box —
pull one from the in-app library and start chatting. Deploy:

    teploy template install open-webui --server <name> --domain ai.example.com

The first account created becomes the administrator.

## Hardware honesty

This is the one template where the "$5 VPS" is not enough. Quantized small
models (1-8B) want roughly 8 GB of RAM to be usable; a GPU makes everything
faster but is not required. Run it on a home server or a beefy box, not the
smallest tier. Models are pulled at runtime and live on the `ollama` volume —
each one is gigabytes, so give the disk room to grow.

## GPU

The template deploys the CPU path with the current Teploy CLI. Changing the
image tag and installing the NVIDIA Container Toolkit does not allocate a
GPU: the CLI has no GPU request field and does not pass Docker's `--gpus`
option. See [Open WebUI's quick start](https://docs.openwebui.com/getting-started/quick-start/)
for the separate runtime and device-allocation requirements. Use a supported
GPU runtime outside this template, or a future, tested CLI GPU feature.

## Alternatives it replaces

ChatGPT/Claude subscriptions for everyday chat, plus a local API endpoint
(Ollama's, on the same container) that other self-hosted apps can call.
