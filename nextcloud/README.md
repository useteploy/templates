# Nextcloud

Self-hosted file sync and sharing (plus calendar, contacts, and a large app
ecosystem). The image is digest-pinned to an `apache` build shipping
PHP 8.5.12 (2026-10-21; see `teploy.yml` for the bump procedure).

Deploy:

    teploy template install nextcloud --server <name> \
      --domain cloud.example.com --var db_password=<choose-one>

Log in as `admin` with the NEXTCLOUD_ADMIN_PASSWORD printed at install, then
install the desktop/mobile sync clients and point them at https://<domain>.
