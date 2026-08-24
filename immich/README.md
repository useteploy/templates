# Immich

Self-hosted photo and video backup — the Google Photos replacement. Deploy:

    teploy template install immich --server <name> \
      --var domain=photos.example.com --var db_password=<choose-one>

First boot downloads ML models and runs migrations (a few minutes). Then open
https://<domain>, create the admin user, and install the Immich mobile app to
start backing up your camera roll.

Photos live in the `immich-upload` volume (`/data` in the container) — size
your server's disk for your library. The `ml` accessory wants ~2GB RAM for
smart search; add `memory:` caps if the server is small.
