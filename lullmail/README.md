# Lull Mail — briefing-first mail client

Screen senders once and route them forever; a daily briefing of what
actually needs you; board/calendar/notes that derive themselves from your
mail. One Go binary + Postgres, AGPL-3.0. Deploy:

    teploy template install lullmail --server <name> \
      --var domain=mail.example.com --var db_password=$(openssl rand -hex 16)

First boot prints a one-time setup token to the logs (`teploy logs`):
paste it in the browser, create your passkey, save the recovery codes.
PUBLIC_URL stays unset - the origin is detected from the setup visit and
pinned, so reach the app through its final domain when you run setup.

Connect mailboxes over IMAP/JMAP immediately. Gmail/Graph OAuth are
bring-your-own-client-ID (see the repo README) - no verification process
needed to self-host.

Source and docs: https://github.com/lullmail/lullmail - site:
https://lullmail.com.
