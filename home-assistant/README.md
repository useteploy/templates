# Home Assistant

Open-source home automation hub. Deploy:

    teploy template install home-assistant --server <name> --var domain=home.example.com

## Required after first deploy

Home Assistant returns `400 Bad Request` to proxied traffic until the proxy
is trusted. Append this to `/config/configuration.yaml` and restart:

    teploy app exec homeassistant -- sh -c 'printf "\nhttp:\n  use_x_forwarded_for: true\n  trusted_proxies:\n    - 172.16.0.0/12\n" >> /config/configuration.yaml'
    teploy app restart homeassistant

Then open https://<domain> and create your user.

Note: on a cloud VPS there are no USB radios (Zigbee/Z-Wave) — this shape is
for network-based integrations, or run it on a home server instead.
