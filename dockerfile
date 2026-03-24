# syntax=docker/dockerfile:1.4
FROM --platform=$BUILDPLATFORM python:3.13-alpine AS builder
FROM python:3.13-alpine

WORKDIR /app

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

COPY . .

EXPOSE 5000

# Run the Flask app with Gunicorn in production mode
ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
