# Paperless-ngx

Document management: scan/drop documents in, get OCR'd, tagged, searchable
archives out. Deploy:

    teploy template install paperless-ngx --server <name> \
      --var domain=docs.example.com --var db_password=<choose-one>

Log in as `admin` with the PAPERLESS_ADMIN_PASSWORD printed at install.
Documents dropped into the `paperless-consume` volume are ingested
automatically.
