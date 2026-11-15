# libteca

One media server for movies, TV, music, audiobooks, podcasts, books, comics
and games, with its own web player. It also speaks the Jellyfin,
Audiobookshelf, OPDS and Subsonic protocols. Deploy:

    teploy template install libteca --server <name> --var admin_password='<choose-one>'

The password must be at least 8 characters. To keep it out of your shell
history, pass it on stdin instead:

    echo '{"admin_password":"<choose-one>"}' | teploy template install libteca --server <name> --var-stdin

Then open `http://<host>:8096` and sign in as `admin`. The administrator is
created on the first start only. Once any user exists the value is ignored,
so changing the password in the web UI is safe.

## Media

Media is read from the `libteca-media` docker volume, mounted at `/media`
inside the container. Copy files in, e.g.:

    docker cp ./movies/. libteca-web-<version>:/media/movies/

or bind a host path instead by editing `volumes:` before deploying. Then add
a library pointing at a folder under `/media` and scan it from the web UI.

The database, covers and caches live in the `libteca-data` volume. That one
volume is the whole backup.

## Network access

Sign-in is required, but the unchanged template publishes port 8096 on all
host interfaces (`0.0.0.0`) over plain HTTP, even on a host that also has
Tailscale. Do not use one-step install on an Internet-reachable host without
a tested network restriction. Ordinary UFW rules do not reliably restrict
Docker-published ports; see [Docker's firewall
notes](https://docs.docker.com/engine/network/packet-filtering-firewalls/#docker-and-ufw).

To limit it to one address, render and retain a manifest in a new private
working directory, set `server:` and an explicit `bind:` to the intended
host loopback or Tailnet IP, then deploy that manifest. There is no template
`--bind` flag. Binding host ingress does not isolate peers on the shared
`teploy` Docker bridge.

## Transcoding

The teploy format has no device mapping, so video transcoding in the
container is software-only. For hardware transcoding, run the binary under
systemd as described in the libteca deploy guide.
