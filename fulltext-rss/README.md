# Full-Text RSS

FiveFilters Full-Text RSS - feeds that only give you the first paragraph come
out the other side with complete articles. Deploy:

    teploy template install fulltext-rss --server <name> --var domain=fulltext.example.com

Use from FreshRSS: subscribe to
`https://<domain>/makefulltextfeed.php?url=<feed-url>` instead of the
original feed (or use FreshRSS's built-in fulltext option per feed).
