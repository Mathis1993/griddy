# Dockerfile for the Django application
FROM python:3.12.1 AS base

# Working directory
RUN mkdir -p /app
WORKDIR /app

COPY ./requirements/. ./requirements/

# Install dependencies
RUN pip install -r requirements/base.txt

COPY . .

# Ensure ownership and permissions (first linux user has usually id 1000)
RUN chown -R 1000:1000 /app && \
    chmod +x /app/scripts/startup_django.sh

LABEL org.opencontainers.image.source="https://github.com/Mathis1993/griddy"

CMD ["scripts/startup_django.sh"]

FROM base AS staging

# Install dependencies
RUN pip install -r requirements/test.txt

CMD ["scripts/startup_django.sh"]
