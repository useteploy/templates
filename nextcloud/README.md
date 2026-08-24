# Nextcloud

Self-hosted file sync and sharing (plus calendar, contacts, and a large app
ecosystem). Deploy:

    teploy template install nextcloud --server <name> \
      --var domain=cloud.example.com --var db_password=<choose-one>

Log in as `admin` with the NEXTCLOUD_ADMIN_PASSWORD printed at install, then
install the desktop/mobile sync clients and point them at https://<domain>.
