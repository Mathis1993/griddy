# griddy
A simple django project for calculating the effect of switching from a static to a dynamic electricity rate in Germany based on somebody's specific personal situation.

![griddy gif](data/griddy.gif)

## Stack
- Python 3.12+
- Django 5.0+
- PostgreSQL
- Tailwind CSS
- Preline UI
- HTMX

## Run
- Create a virtual environment (python 3.12 or higher) and install the requirements:
  ```bash
  python -m venv venv
  source venv/bin/activate
  pip install -r requirements/test.txt
  ```
- Copy over the example environment file:
  ```bash
  cp .env-sample .env
  ```
- Create a fernet key (used to encrypt db ids in urls):
  ```bash
  bash fernet.sh
  ```
- Grab the key from the terminal output and set it as the value of the `FERNET_KEY` variable in the `.env` file
- Start docker containers:
  ```bash
  docker compose up -d
  ```
- Run migrations and seed data:
  ```bash
  bash nuke.sh
  ```
- Run the server:
  ```bash
  python manage.py runserver
  ```

**Note: When running the calculation for the first time, it will take a while, because historical energy price data has to be fetched.**

### JS Toolchain
Concept: https://stackoverflow.com/questions/63392426/how-to-use-tailwindcss-with-django#63392427

Prerequisites:
- Install `node` and `npm`
- Install `tailwindcss` (`npm install tailwindcss`)

Build:
- `cd jstoolchain`
- `npm run tailwind-build`
- `npm run js-build`
