# gsheir.com

My personal website to host portfolios and random games.

## Run using Docker

Make sure you [have Docker installed](https://docs.docker.com/desktop/).

In the root directory, run:
```bash
docker compose up
```

The web app will be available at `http://localhost:8000/`

## Deployment

### Railway (Recommended)

This application is optimized for Railway deployment. See [DEPLOYMENT_RAILWAY.md](./DEPLOYMENT_RAILWAY.md) for detailed instructions.

### Local Development

1. **Environment Setup**
   ```bash
   cp .env.example .env
   ```
   Edit .env with your local settings

2. **Database Migration**
   ```bash
   docker compose exec web python manage.py migrate
   ```

3. **Create Superuser**
   ```bash
   docker compose exec web python manage.py createsuperuser
   ```


## Data Management

### Sync with FBRef API

This application can sync with [FBR API](https://fbrapi.com/) for football data:

```bash
docker compose exec web python manage.py sync_fbr_data
```

### Process Round Results

Calculate points and update team selections:

```bash
docker compose exec web python manage.py process_round
```

## Admin Interface

Access the admin interface at `/admin/` to:
- Manage users, leagues, and teams
- Input match results manually
- View comprehensive match management interface
- Process rounds and calculate points

## License

This project is for personal use.
