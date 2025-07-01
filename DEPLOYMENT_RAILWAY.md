# Railway Deployment Guide

This document explains how to deploy the Women's Euro 2025 Fantasy Game to Railway.

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app) using GitHub
2. **GitHub Repository**: Push your code to GitHub
3. **Docker**: Your project is already configured for Docker deployment

## Step-by-Step Deployment

### 1. Create Railway Account
- Go to [railway.app](https://railway.app)
- Click "Login" and sign in with GitHub
- Authorize Railway to access your repositories

### 2. Create New Project
- Click "New Project" in Railway dashboard
- Select "Deploy from GitHub repo"
- Choose your `gsheir.com` repository
- Railway will detect the Dockerfile automatically

### 3. Add PostgreSQL Database
- In your Railway project dashboard, click "New Service"
- Select "Database" → "Add PostgreSQL"
- Railway will automatically create a PostgreSQL instance
- The `DATABASE_URL` environment variable will be set automatically

### 4. Configure Environment Variables
Go to your web service → "Variables" tab and add these environment variables:

```env
SECRET_KEY=your-super-secret-key-generate-a-strong-one
DEBUG=False
ALLOWED_HOSTS=*.up.railway.app,*.railway.app,gsheir.com,www.gsheir.com
FBR_API_KEY=your-fbr-api-key-here
RAILWAY_ENVIRONMENT=production
```

**Important**: Generate a strong `SECRET_KEY` for production. You can use:
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### 5. Deploy
- Railway will automatically deploy when you push to your main branch
- First deployment may take 5-10 minutes
- Watch the deployment logs in Railway dashboard

### 6. Run Initial Setup
After first deployment, you may need to create a superuser:

1. Go to your Railway project dashboard
2. Open the web service
3. Go to "Deploy" tab → click on latest deployment
4. Click "View Logs" 
5. If needed, you can create a superuser by going to "Settings" → "Environment" and temporarily adding:
   ```
   DJANGO_SUPERUSER_USERNAME=your_username
   DJANGO_SUPERUSER_EMAIL=your_email@example.com
   DJANGO_SUPERUSER_PASSWORD=your_password
   ```
6. Redeploy, then remove these variables after the superuser is created

### 7. Custom Domain (Optional)
- In Railway dashboard, go to "Settings" → "Domains"
- Click "Custom Domain" and add `gsheir.com`
- Follow Railway's instructions to update your DNS records

## Environment Variables Reference

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Django secret key for cryptographic signing | ✅ |
| `DEBUG` | Set to `False` for production | ✅ |
| `DATABASE_URL` | PostgreSQL connection URL (auto-provided by Railway) | ✅ |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts | ✅ |
| `FBR_API_KEY` | API key for FBRef data (if using external data) | ❌ |
| `RAILWAY_ENVIRONMENT` | Set to `production` | ✅ |

## File Structure for Railway

The following files are configured for Railway deployment:

- `Dockerfile` - Optimized for Railway with PORT variable support
- `railway.json` - Railway-specific deployment configuration
- `requirements.txt` - Python dependencies (exported from Poetry)
- `.dockerignore` - Excludes unnecessary files from Docker build
- `.env.example` - Template for environment variables

## Monitoring and Logs

- **Deployment Logs**: Railway dashboard → Deploy tab → View logs
- **Application Logs**: Railway dashboard → Deploy tab → Latest deployment logs
- **Metrics**: Railway provides automatic monitoring of CPU, memory, and network

## Troubleshooting

### Common Issues

1. **Build fails**: Check that all dependencies are in `requirements.txt`
2. **Database connection error**: Ensure PostgreSQL service is running and `DATABASE_URL` is set
3. **Static files not loading**: Railway handles static files automatically via WhiteNoise
4. **Port binding error**: Railway sets `PORT` environment variable automatically

### Database Commands

If you need to run management commands:
1. Go to Railway dashboard → your service → Deploy tab
2. Click on latest deployment → View logs
3. The deployment automatically runs migrations on startup

### Redeployment

- **Automatic**: Push to main branch triggers redeployment
- **Manual**: Railway dashboard → Deploy tab → "Redeploy"

## Security Notes

- Never commit secrets to the repository
- Use strong passwords and secret keys
- Railway provides HTTPS automatically
- Database connections are encrypted
- Environment variables are securely stored

## Support

- Railway Documentation: [docs.railway.app](https://docs.railway.app)
- Railway Community: [Railway Discord](https://discord.gg/railway)
- Project Issues: Create issues in your GitHub repository
