# gsheir.com

My personal website to host portfolios and random games.

# Women's Euro 2025 game

## Run using Docker

Make sure you [have Docker installed](https://docs.docker.com/desktop/).

In the root directory of this repo, run `docker compose up`.

The web app should be available to view on `http://0.0.0.0:8080/`.


## Sync data with FBRef

This application uses [FBR API](https://fbrapi.com/) to get football data. Run the syncing with the following command:

```
docker compose exec web poetry run python manage.py sync_fbr_data
```
