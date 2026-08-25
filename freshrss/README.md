# FreshRSS

Self-hosted RSS reader. Deploy:

    teploy template install freshrss --server <name> --var domain=rss.example.com

First visit runs the install wizard - keep SQLite (default) and create your
user. Feeds refresh automatically via the built-in cron (CRON_MIN env).
Pairs well with the rsshub and fulltext-rss templates: RSSHub invents feeds
for sites that lack them, Full-Text RSS un-truncates stingy ones.
