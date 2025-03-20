# syntax=docker/dockerfile:1.4
FROM --platform=$BUILDPLATFORM python:3.10-alpine AS builder

WORKDIR /app

COPY requirements.txt /app
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt gunicorn

COPY . /app

# Expose port 5000 inside the container
EXPOSE 5000

# Run the Flask app with Gunicorn in production mode
ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]