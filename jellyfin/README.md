# Jellyfin

Free software media server. Deploy:

    teploy template install jellyfin --server <name> --var domain=media.example.com

First visit runs the setup wizard (create your admin user there).

Media is stored in the `jellyfin-media` docker volume, mounted at `/media`
inside the container. Get files into it, e.g.:

    docker cp ./movies/. jellyfin-web-<version>:/media/movies/

or bind a host path instead by editing `volumes:` before deploying.
