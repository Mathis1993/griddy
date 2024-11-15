# griddy
Welcome to griddy - a simple django/tailwind project for calculating the effect of switching to a dynamic electricity rate based on somebody's specific personal situation.

## Docs
See the `docs` directory in this repo and the `obsidian` vault backed up to [Mathis1993/obsidian](https://github.com/Mathis1993/obsidian).

## Stack
This is a simple template for a django project using
- `tailwind CSS`
- `docker compose`
- a `postgres` database
- session-based authentication (via the database)
- `pytest` and `factory-boy` for testing
- `github actions` CI/CD
- `sendgrid` for sending emails
- `celery` for asynchronous tasks (probably later)
- `sentry` for error tracking (probably later)
- `traefik` as a reverse proxy (probably later)
- `letsencrypt` for SSL certificates (probably later)

## Variables
The following variables need still to be replaced :
- `production_domain` -> Your domain for the production system
- `staging_domain` -> Your domain for the staging system
- `certs_email` -> The email address for the letsencrypt certificates
