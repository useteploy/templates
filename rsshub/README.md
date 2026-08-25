# RSSHub

Feed generator for the feedless web - thousands of routes turn YouTube
channels, GitHub activity, social accounts and more into RSS. Deploy:

    teploy template install rsshub --server <name> --var domain=rsshub.example.com

Browse routes at docs.rsshub.app, then subscribe in FreshRSS as
`https://<domain>/<route>`. Consider an access: basic_auth gate if you don't
want the public using your instance.
