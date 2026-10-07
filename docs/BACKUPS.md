# Backup scope per template

What each template persists, and what to back up before upgrading it.
Catalog CI checks structure, rendering and documented command admission;
it does not prove that an application can be installed or restored.

## Prerequisites

- Run the normal backup commands from a directory containing the matching
  `teploy.yml`, including the deployed `app`, its `domain` (or host ingress
  and port), `server`, and accessory definitions. `--host` can override a
  configured server, but does not replace the required local configuration.
- One-step `teploy template install` does **not** save that manifest locally.
  Follow the one-step-install section below if you do not have it. Do not
  re-render a template to recover credentials: `generate` values change.
- Choose an existing S3 bucket and region, configure the server's AWS
  credentials/role with the required bucket permissions, and ensure the AWS
  CLI is already installed on the server. Commands below do not provision
  a bucket, install software, or configure credentials.
- Replace `<bucket>`, `<region>`, `<name>` and other placeholders before
  running commands. For S3-compatible storage, also pass `--endpoint <url>`
  and set `TEPLOY_S3_ACCESS_KEY` / `TEPLOY_S3_SECRET_KEY` (or the supported
  `AWS_*` equivalents) securely in the calling environment. Those local
  credentials are forwarded only for custom endpoints; plain AWS uses the
  server's credential chain. Do not put secrets in shell history or Git.

## What Teploy backs up

- `teploy backup create --bucket <bucket> --region <region>` archives the
  app's managed volumes directory plus the app-level `.env`. App volumes
  are host bind mounts under `/deployments/<app>/volumes/`, not Docker named
  volumes. This is a live file copy, not a database-consistency guarantee;
  quiesce writers or use a database-native consistent backup first.
- `teploy accessory backup <accessory> --bucket <bucket> --region <region>`
  selects an engine-aware dump for recognized PostgreSQL, MySQL/MariaDB,
  MongoDB and Redis images. The accessory name is positional; for many
  templates it is `db`. Other image names, including Nucleus and Valkey,
  take the generic accessory-volume archive path. PostgreSQL protocol
  compatibility alone does not select `pg_dump`.
- Accessory data under `/deployments/<app>/accessories/` is not part of the
  ordinary app-volume archive. Back it up separately when needed. A generic
  archive of a running engine is not a verified, consistent database dump.
- Restore commands are `teploy backup restore <date> --bucket <bucket>
  --region <region>` and `teploy accessory restore <accessory> <date>
  --bucket <bucket> --region <region>`. These replace live data: rehearse on
  an isolated scratch deployment, with writers stopped and the right
  application/engine version. Use each artifact's actual timestamp; a dump
  and volume archive may have different IDs. A successful command alone
  does not prove application recovery. See `AUDIT_OPEN.md` for remaining
  recovery/persistence limitations; do not treat this checklist as a fix
  for the CLI's outstanding backup/restore defects.

## After a one-step install

The safest long-term workflow is to retain the exact rendered deployment
manifest and generated credentials from the start, with private permissions
and outside version control. For an existing one-step installation:

1. If the original manifest was retained separately, use that matching copy.
2. Otherwise, create a separate **backup-only** working directory. A minimal
   `teploy.yml` can identify the existing app/server and accessory images
   without regenerating secrets. For example, for an unchanged Ghost
   installation, replace the domain/server below with the real values:

   ```yaml
   # BACKUP ONLY: never run deploy/apply from this directory.
   app: ghost
   domain: blog.example.com
   server: my-server
   accessories:
     db:
       image: mysql:8
   ```

   Match the actual deployed app name, ingress, port (for host ingress),
   domain, server and accessory keys/images. The backup command archives
   the server's existing managed app-volume tree; no `volumes:` declaration
   is needed in this backup-only file. Normal accessory backup inspects the
   running accessory for its actual image/environment. Confirm the intended
   database is running first; if inspection fails or a fallback-to-config
   message appears, stop and recover the real configuration instead of
   guessing credentials. This file is not a deployment or restore manifest.
3. For an accessory-only backup without a local manifest, the server itself
   can run the following if Teploy and AWS CLI are already installed there
   and the accessory is running:

       teploy accessory backup db --local --app <app> --bucket <bucket> --region <region>

   Run this **on that server**; `--local` means its local Docker daemon.
   `--app` alone on a remote backup does not bypass local config loading.
   Ordinary app-volume backup and accessory restore have no equivalent
   state-only path. Keep/recover configuration for a tested restore.

## Pre-upgrade checklist

1. Verify the prerequisites and choose a maintenance window. Follow the
   upstream application's consistency procedure. For SQLite/file databases,
   stop writes or create a native consistent snapshot; for database-plus-file
   apps, coordinate the dump and files. Keep database accessories running
   while taking engine-aware dumps.
2. From the matching manifest directory, back up each required accessory:

       teploy accessory backup db --bucket <bucket> --region <region>

   Replace `db` with the real key (for example `nucleus`), and remember that
   unrecognized engines receive a generic archive, not an engine-aware dump.
3. For apps with managed app volumes, take the file backup in the same
   consistency window:

       teploy backup create --bucket <bucket> --region <region>

   Skip this for stateless apps and templates without managed app volumes;
   it does not capture unmanaged/anonymous Docker volumes.
4. Confirm the uploaded artifacts and rehearse recovery in a scratch
   deployment before upgrading production. Where supported, use:

       teploy accessory verify-backup db --bucket <bucket> --region <region>

   This accessory check does not verify the app files or a complete recovery.
5. Upgrade, verify actual application data and behavior, and keep previous
   backups until recovery is proven. Container health alone is insufficient.

## Per-template state

| Template | Managed app volumes | DB/accessory backup | Notes |
|---|---|---|---|
| immich | upload (photos/videos) | db (postgres, vector extensions) | upload + db dump together; ml cache is rebuildable |
| nextcloud | data (/var/www/html) | db (postgres); redis (Valkey) is cache-only | use upstream maintenance/backup procedure |
| paperless-ngx | data, media, export | db (postgres); redis (Valkey) | documents live in media; export dir is the migration path |
| postgres-admin | — | db (postgres) | back up via the db accessory only |
| wordpress | **none configured** | db (mysql) | database dump excludes uploads/plugins/themes; current template's anonymous WordPress volume needs a separate consistent backup and a deliberate persistence migration before redeploy (TPL-01 remains open) |
| ghost | content (images/themes) | db (mysql) | posts in db; uploads in content |
| lullmail | appdata | db (postgres) | mail state in db dump + appdata |
| teploy-ship | ship-data | nucleus (generic volume archive, not pg_dump) | both stores needed; coordinate writes and test engine recovery |
| vaultwarden | data (encrypted vault) | — | preserve database and attachments consistently |
| home-assistant | config | — | includes configuration and recorder database; quiesce writes |
| jellyfin | config, cache, media | — | config/database and media matter; cache is rebuildable |
| audiobookshelf | config, metadata, audiobooks, podcasts | — | database/listening progress in config; preserve metadata and media too |
| kavita | config, books | — | library files + config/database |
| syncthing | data (/var/syncthing) | — | includes device identities/keys and synced files |
| actual-budget | data | — | includes server settings/account database and budget files |
| freshrss | data (SQLite), extensions | — | use a database-consistent copy |
| open-webui | open-webui (app data), ollama (models) | — | app database needs consistency; model files are re-downloadable |
| ollama | ollama (models + config) | — | models re-downloadable; preserve configuration |
| rsshub | — | — | stateless (cache in-container) |
| fulltext-rss | — | — | stateless |
