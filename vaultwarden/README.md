# Vaultwarden

Bitwarden-compatible password manager (all official Bitwarden apps and
browser extensions work against it). Deploy:

    teploy template install vaultwarden --server <name> --var domain=vault.example.com

The generated ADMIN_TOKEN is printed once at install — it is the login for
`https://<domain>/admin`. After creating your user accounts, set
`SIGNUPS_ALLOWED=false` (admin panel or env) so strangers can't register.
