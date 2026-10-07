# Home Assistant

Open-source home automation hub. Deploy:

    teploy template install home-assistant --server <name> --domain home.example.com

## Required after first deploy

Home Assistant returns `400 Bad Request` to proxied traffic until the proxy
is trusted. One-step install does not retain a local `teploy.yml`, so use
explicit app and host selectors for the following commands. Replace
`<name>` with the same server name used at install.

First check the installed Home Assistant version. The floating `stable`
image does not imply that an old YAML-only repair is still supported.

### Home Assistant 2026.8 and newer

HTTP settings are managed in **Settings → System → Network → HTTP server**.
To reach the UI before proxy trust is configured, inspect the running web
container's loopback-published port:

    teploy exec <name> -- 'docker ps --filter label=teploy.app=homeassistant --filter label=teploy.process=web --format "{{.Names}} {{.Ports}}"'

Use the host port from the `127.0.0.1:<published-port>->8123/tcp` mapping.
With no deployment in progress, establish a local-only tunnel from your
computer using the server's actual SSH host/user (a Teploy server nickname
is not necessarily an SSH alias):

    ssh -N -L 127.0.0.1:18123:127.0.0.1:<published-port> <ssh-user>@<ssh-host>

Add the appropriate `-i` identity option if needed. Open
`http://127.0.0.1:18123`, complete first-user setup, then enable **Trust
X-Forwarded-For** and add only the verified proxy source to **Trusted
proxies**. Saving restarts Home Assistant; confirm the settings in the UI
within five minutes or they revert. Keep the tunnel available until the
proxied domain works, then close it. Do not publish a new public port.

An old `http:` YAML block is imported once during migration and ignored on
subsequent starts. Follow the [current HTTP documentation](https://www.home-assistant.io/integrations/http/)
for migration/repair rather than appending YAML after migration.

### Older releases using YAML HTTP configuration

Read the current configuration and save a copy before editing:

    teploy app exec --app homeassistant --host <name> -- 'cat /config/configuration.yaml'
    teploy app exec --app homeassistant --host <name> -- 'cp -p /config/configuration.yaml /config/configuration.yaml.before-proxy'

Keep the backup until the new configuration is verified; do not overwrite
it when retrying a failed edit. On the server, edit the persisted file
`/deployments/homeassistant/volumes/config/configuration.yaml`. Merge this
into an existing `http:` section, or add one if absent; do not append a
second `http:` key:

```yaml
http:
  use_x_forwarded_for: true
  trusted_proxies:
    - REPLACE_WITH_ACTUAL_PROXY_IP
```

Replace the placeholder with the proxy source address reported by Home
Assistant's untrusted-proxy error, after confirming it belongs to your
proxy. Use this same check for the UI workflow above. Inspect the logs with:

    teploy logs --app homeassistant --host <name>

Trust only the actual proxy address or a deliberately scoped proxy subnet,
not all of `172.16.0.0/12`. Teploy's Docker bridge is shared with other apps;
it is not an app-private trust boundary. See the [Home Assistant HTTP
configuration](https://www.home-assistant.io/integrations/http/) for proxy
requirements for your installed version. For this legacy YAML workflow,
restart:

    teploy restart --app homeassistant --host <name>

Check the logs for configuration errors, then open https://<domain> and
create your user if needed. Recheck proxy trust if the proxy's source
address changes.

Note: on a cloud VPS there are no USB radios (Zigbee/Z-Wave). This template
uses bridge networking, not host networking; local multicast discovery and
USB passthrough are not configured. Use network integrations that work with
this topology, or plan a separate local-device deployment.
