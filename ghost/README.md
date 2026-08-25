# Ghost

Modern publishing platform - blog, memberships, and a built-in newsletter.
Deploy:

    teploy template install ghost --server <name> \
      --var domain=blog.example.com --var db_password=<choose-one>

Create the admin account at https://<domain>/ghost within the first minutes
of the deploy (setup is first-come-first-served). Email sending for
newsletters needs SMTP credentials - add mail__* env vars when you get there.
