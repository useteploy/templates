# Backup scope per template

What each template persists, and what to back up before upgrading it.
The catalog CI (`.github/workflows/validate.yml`) keeps templates
renderable, but data safety is an operational contract, not a CI one:
every stateful template below assumes a backup taken before an upgrade.

## What teploy backs up

- `teploy backup create` — the app's volumes directory plus the app-level
  `.env` (recent teploy builds archive the `.env` and restore it at its
  app-level location with the previous copy kept as `.env.pre-restore`;
  older builds left the `.env` untouched on restore).
  This is a file copy: correct for uploaded media, documents, and config;
  only crash-consistent for a database engine that is running.
- `teploy accessory backup --accessory <name>` — engine-aware dump of a
  database accessory (pg_dump / mysqldump / mongodump / redis bgsave).
  For anything with a `db` accessory below, THIS is the backup that
  restores cleanly into a fresh deployment; run it in addition to
  `backup create`.
- `teploy backup restore <date>` / `teploy accessory restore` — restore
  volumes/.env and engine dumps respectively. Restoring a database dump
  into a running engine is supported; test on a scratch app first.

Pre-upgrade checklist for every stateful template below:

1. `teploy accessory backup --accessory db` (when a db accessory exists)
2. `teploy backup create`
3. upgrade, then verify health before pruning old backups

## Per-template state

| Template | Volumes (what it holds) | DB accessory | Notes |
|---|---|---|---|
| immich | upload (photos/videos) | db (postgres, vector extensions) | upload + db dump together; the ml cache volume is rebuildable |
| nextcloud | data (/var/www/html) | db (postgres), redis | file data + db dump; redis is cache-only |
| paperless-ngx | data, media, export | db (postgres), redis | documents live in media; export dir is the migration path |
| postgres-admin | — | db (postgres) | back up via the db accessory only |
| wordpress | — | db (mysql) | all content is in the db dump |
| ghost | content (images/themes) | db (mysql) | posts in db; uploads in content |
| lullmail | appdata | db (postgres) | mail state in db dump + appdata |
| teploy-ship | ship-data | nucleus (postgres API) | runs + store; both needed to rebuild |
| vaultwarden | data (encrypted vault) | — | the volume IS the vault; back it up before every upgrade |
| home-assistant | config | — | full state in the volume |
| jellyfin | config, cache, media | — | config matters; media is your own; cache rebuildable |
| audiobookshelf | config, metadata, audiobooks | — | listening progress lives in metadata |
| kavita | config, books | — | library files + config |
| syncthing | data (/var/syncthing) | — | device identities/keys live in this volume |
| actual-budget | data | — | budget files |
| freshrss | data (SQLite lives here), extensions | — | SQLite file must be copied, not written concurrently |
| open-webui | open-webui (app data), ollama (models) | — | model files are large; re-downloadable |
| ollama | ollama (models + config) | — | models re-downloadable; config small |
| rsshub | — | — | stateless (cache in-container) |
| fulltext-rss | — | — | stateless |
