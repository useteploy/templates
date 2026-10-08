# WordPress

The template persists MySQL data and the whole `/var/www/html` directory in
managed volumes. Back up both together: the database dump alone excludes
uploads, plugins and themes. Use a password containing only hexadecimal
characters until your CLI supports literal secret rendering through all
substitution and deployment steps.

    teploy template install wordpress --server <name> --domain blog.example.com \
      --var db_password=$(openssl rand -hex 16)

## Existing installations: migrate before redeploy

Older catalog versions let the WordPress image create an anonymous volume.
Adding the managed mount hides that existing directory; Docker does not copy
an old container's anonymous volume into the new Teploy volume. Do this on the
selected deployment host, before upgrading the manifest:

1. Put the site into maintenance, stop writers and record the current app
   container and image version. Inspect that exact container's mounts with
   `docker inspect` to identify the volume mounted at `/var/www/html`; do not
   guess its name or select a different app's volume.
2. Keep the stopped container and old volume. Make a MySQL backup and copy
   the complete directory from the stopped container with `docker cp -a
   <container>:/var/www/html/. <private-backup-directory>/`. Preserve numeric
   ownership, modes, symlinks and hidden files; verify the backup before
   proceeding. Retain credentials privately with the restore material.
3. Create the new Teploy managed source directory shown by the deployment
   plan (`/deployments/wordpress/volumes/wordpress` for an app named
   `wordpress`). Copy the verified backup with `rsync -aH --numeric-ids
   <private-backup-directory>/ /deployments/wordpress/volumes/wordpress/`
   as a user allowed to preserve numeric ownership and permissions. Compare
   numeric uid/gid, modes, symlink targets, hidden files and file hashes
   between the stopped source, backup and destination before starting it. Refuse a nonempty destination unless its
   contents have been inspected and separately backed up.
4. Deploy the updated manifest, inspect the new container's mount, and
   verify the existing site, media, administrator login, plugins and themes.
   Keep the old container, anonymous volume and database backup until this
   validation succeeds. Do not delete the old volume during the migration.
5. If validation fails, stop the new app and return to the old container and
   old mount. Restore the matching database backup if the new image changed
   its schema; an image rollback alone cannot reverse database migrations.

Rehearse backup and restore on a disposable host using representative content
before upgrading a production site. See [backup scope](../docs/BACKUPS.md).
