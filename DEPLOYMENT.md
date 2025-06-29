# Cloud Deployment Guide

This Django application uses Poetry for dependency management and is designed to be easily deployed to cloud platforms without requiring a persistent server.

## Pre-deployment Setup

### Export requirements.txt for platforms that don't support Poetry:

```bash
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

Note: Some cloud platforms still require requirements.txt, so we maintain this file for compatibility.

## Railway Deployment (Recommended)

Railway provides automatic Django deployment with minimal configuration:

1. **Connect Repository**
   - Visit [railway.app](https://railway.app)
   - Connect your GitHub repository
   - Railway will auto-detect Django and configure deployment

2. **Environment Variables**
   Set these in Railway's dashboard:
   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=False
   FBR_API_KEY=your-fbr-api-key
   ALLOWED_HOSTS=your-app.railway.app
   ```

3. **Database**
   - Add PostgreSQL plugin in Railway dashboard
   - DATABASE_URL will be automatically set

4. **Deploy**
   - Push to main branch
   - Railway automatically deploys

## Heroku Deployment

1. **Install Heroku CLI**
   ```bash
   # macOS
   brew tap heroku/brew && brew install heroku
   ```

2. **Create App**
   ```bash
   heroku create your-app-name
   ```

3. **Add PostgreSQL**
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```

4. **Set Environment Variables**
   ```bash
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set DEBUG=False
   heroku config:set FBR_API_KEY=your-api-key
   ```

5. **Deploy**
   ```bash
   git push heroku main
   heroku run python manage.py migrate
   heroku run python manage.py createsuperuser
   ```

## Render Deployment

1. **Connect Repository**
   - Visit [render.com](https://render.com)
   - Create new Web Service from GitHub

2. **Build Settings**
   - Build Command: `pip install poetry && poetry config virtualenvs.create false && poetry install --no-dev`
   - Start Command: `poetry run gunicorn weuro2025.wsgi:application`
   - Or if using requirements.txt: `pip install -r requirements.txt`

3. **Environment Variables**
   Set in Render dashboard:
   ```
   SECRET_KEY=your-secret-key
   DEBUG=False
   FBR_API_KEY=your-api-key
   PYTHON_VERSION=3.11.0
   ```

4. **Database**
   - Create PostgreSQL database in Render
   - Copy DATABASE_URL to web service environment

## DigitalOcean App Platform

1. **Connect Repository**
   - Visit DigitalOcean App Platform
   - Connect GitHub repository

2. **App Configuration**
   ```yaml
   name: weuro2025-game
   services:
   - name: web
     source_dir: /
     github:
       repo: your-username/your-repo
       branch: main
     run_command: gunicorn weuro2025.wsgi:application
     environment_slug: python
     instance_count: 1
     instance_size_slug: basic-xxs
     env:
     - key: SECRET_KEY
       value: your-secret-key
     - key: DEBUG
       value: "False"
     - key: FBR_API_KEY
       value: your-api-key
   databases:
   - name: db
     engine: PG
     num_nodes: 1
     size: db-s-dev-database
   ```

## AWS Elastic Beanstalk

1. **Install EB CLI**
   ```bash
   pip install awsebcli
   ```

2. **Initialize**
   ```bash
   eb init
   eb create weuro2025-env
   ```

3. **Configure**
   Create `.ebextensions/django.config`:
   ```yaml
   option_settings:
     aws:elasticbeanstalk:container:python:
       WSGIPath: weuro2025.wsgi:application
     aws:elasticbeanstalk:application:environment:
       DJANGO_SETTINGS_MODULE: weuro2025.settings
   ```

4. **Deploy**
   ```bash
   eb deploy
   ```

## Google Cloud Run

1. **Build Container**
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT-ID/weuro2025
   ```

2. **Deploy**
   ```bash
   gcloud run deploy --image gcr.io/PROJECT-ID/weuro2025 --platform managed
   ```

3. **Database**
   - Create Cloud SQL PostgreSQL instance
   - Connect via Cloud SQL Proxy

## Post-Deployment Setup

After deploying to any platform:

1. **Run Migrations**
   ```bash
   # With Poetry
   poetry run python manage.py migrate
   
   # Or with pip
   python manage.py migrate
   ```

2. **Create Superuser**
   ```bash
   # With Poetry
   poetry run python manage.py createsuperuser
   
   # Or with pip
   python manage.py createsuperuser
   ```

3. **Sync Initial Data**
   ```bash
   # With Poetry
   poetry run python manage.py sync_fbr_data
   
   # Or with pip
   python manage.py sync_fbr_data
   ```

4. **Set Up Scheduled Tasks**
   Configure platform-specific cron jobs or scheduled tasks:
   - Sync data: `poetry run python manage.py sync_fbr_data` (hourly)
   - Process rounds: `poetry run python manage.py process_round` (every 10 minutes)

## Docker Deployment

The project includes Docker support with Poetry integration:

### Development with Docker

```bash
# Build and run with development settings
docker-compose -f docker-compose.dev.yml up --build

# Or use regular docker-compose
docker-compose up --build
```

### Production Docker Build

```bash
# Build production image
docker build -t weuro2025-game .

# Run production container
docker run -p 8000:8000 \
  -e SECRET_KEY=your-secret-key \
  -e DATABASE_URL=your-database-url \
  -e FBR_API_KEY=your-api-key \
  weuro2025-game
```

### Multi-stage Poetry Build

For optimized production builds, use the Poetry-specific Dockerfile:

```bash
docker build -f Dockerfile.poetry -t weuro2025-game .
```

## Domain Configuration

For custom domain (gsheir.com/weuro2025_game):

1. **DNS Setup**
   - Add CNAME record pointing to your app's URL
   - For subdirectory routing, configure your main site to proxy `/weuro2025_game/` to the Django app

2. **HTTPS**
   - Most platforms provide automatic HTTPS
   - Update ALLOWED_HOSTS to include your domain

3. **Static Files**
   - Ensure STATIC_ROOT is configured
   - Run `collectstatic` during build

## Monitoring & Maintenance

- Set up application monitoring (New Relic, Sentry)
- Configure log aggregation
- Set up uptime monitoring
- Schedule regular database backups
- Monitor API usage and costs

## Scaling Considerations

- Use Redis for caching if needed
- Consider CDN for static files
- Database connection pooling for high traffic
- Horizontal scaling with load balancers

Each platform has its own advantages:
- **Railway**: Simplest setup, great for beginners
- **Heroku**: Mature platform, extensive add-ons
- **Render**: Good balance of features and pricing
- **DigitalOcean**: Transparent pricing, good documentation
- **AWS/GCP**: Most powerful, complex configuration
