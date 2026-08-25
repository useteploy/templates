# Audiobookshelf

Self-hosted audiobook and podcast server, with mobile apps that sync your
listening position. Deploy:

    teploy template install audiobookshelf --server <name> --var domain=listen.example.com

First visit creates the admin account. Add podcast RSS feeds in-app (they
auto-download into the `audiobookshelf-podcasts` volume); copy audiobooks into
the `audiobookshelf-audiobooks` volume, e.g.:

    docker cp ./mybook audiobookshelf-web-<version>:/audiobooks/

Apps: Audiobookshelf on Android/iOS, or plappa (iOS).
