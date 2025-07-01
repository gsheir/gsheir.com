# Run migrations
poetry run python manage.py migrate

# Run FBRef sync to initialise database
poetry run python manage.py sync_fbr_data