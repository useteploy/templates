# Lull Mail — briefing-first mail client

Screen senders once and route them forever; a daily briefing of what
actually needs you; board/calendar/notes that derive themselves from your
mail. One Go binary + Postgres, FSL-1.1-MIT. Deploy:

    teploy template install lullmail --server <name> \
      --domain mail.example.com --var db_password=$(openssl rand -hex 16)

DATABASE_URL carries the database host and user; PGPASSWORD supplies the same
password used by the PostgreSQL accessory. Keeping the password out of the URI
preserves characters such as `#`, `/`, `?` and `%` without URL escaping.

First boot prints a one-time setup link to the logs (valid 24 hours). Read
them with the same server name used at install:

    teploy logs --app lullmail --host <name>

The link ends in `/#setup=<token>`. Open it on your domain - for example
`https://mail.example.com/#setup=<token>` - then pick a name and a password
and save the recovery codes. (Pasting the token into the setup screen works
too.) The link dies the moment the account exists; a passkey or an
authenticator app can be added afterwards under Security. PUBLIC_URL stays
unset - the origin is detected from the setup visit and pinned, so reach the
app through its final domain when you run setup.

Connect mailboxes over IMAP/JMAP immediately. Gmail/Graph OAuth are
bring-your-own-client-ID (see the repo README) - no verification process
needed to self-host.

Source and docs: https://github.com/lullmail/lullmail - site:
https://lullmail.com.
