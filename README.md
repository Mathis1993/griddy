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

## JS Toolchain
Concept: https://stackoverflow.com/questions/63392426/how-to-use-tailwindcss-with-django#63392427

Prerequisites:
- Install `node` and `npm`
- Install `tailwindcss` (`npm install tailwindcss`)

Build:
- `cd jstoolchain`
- `npm run tailwind-build`
- `npm run js-build`

## Overriding Django Widget Templates
1. Add `django.forms` to the `INSTALLED_APPS` in `base.py`
2. Add `FORM_RENDERER = "django.forms.renderers.TemplatesSetting"` to `base.py`
3. Create a path `django/forms/widgets` in your `templates` directory
- Override the widget templates you want to change (https://docs.djangoproject.com/en/5.1/ref/forms/widgets/#built-in-widgets) **OR**
- Create a new widget class inheriting from the original widget and override the `template_name` attribute (and others if necessary)