# gsheir.com

Personal portfolio website for Geoffrey Sheir.

## Deployment

### Railway

This application is deployed and hosted with Railway. The application is available at [gsheir.com](https://gsheir.com).

### Local Development

A Docker Compose configuration is provided for local development.

Prerequisites:
- [Docker Desktop](https://docs.docker.com/desktop/) installed and running

Setup:

1. Copy environment variables to local `.env`
   ```bash
   cp .env.example .env
   ```

2. Run Docker Compose
   ```bash
   docker compose up
   ```

   The web app will be available at `http://localhost:8080/`

