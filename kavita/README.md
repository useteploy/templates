# Kavita

Reading server for ebooks, comics, and manga - a fast web reader with
per-user progress and OPDS feeds. Deploy:

    teploy template install kavita --server <name> --var domain=read.example.com

First visit creates the admin account. Copy books into the `kavita-books`
volume, e.g.:

    docker cp ./library/. kavita-web-<version>:/books/

then add `/books` as a library in the admin dashboard. Reading apps that
speak OPDS (KOReader, Panels, etc.) can pull straight from your server.
