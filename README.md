# Women's Euro 2025 Game

A Django-based prediction game for the Women's Euro 2025 tournament. Users create or join leagues and predict which players will score in each round to compete for points.

## Features

- **User Authentication**: Registration and login system
- **League Management**: Create private leagues with unique codes or join existing ones
- **Player Selection**: Select 3 players per round with provisional selection lists
- **Automatic Processing**: Selection confirmation and point calculation based on actual match results
- **Real-time Data**: Integration with FBRef API for player and match data
- **Responsive Design**: Clean, typography-focused UI with sans-serif fonts

## Tech Stack

- **Backend**: Django 4.2, Python 3.8+
- **Database**: PostgreSQL (with SQLite fallback for development)
- **API Integration**: FBRef API for football data
- **Frontend**: HTML5, CSS3, vanilla JavaScript
- **Deployment**: Configured for cloud hosting (Heroku, Railway, etc.)

## Quick Start

### 1. Clone and Setup Environment

```bash
git clone <repository-url>
cd gsheir.com

# Install Poetry if not already installed
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install
```

### 2. Environment Configuration

Copy the example environment file and configure:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=postgres://username:password@localhost:5432/weuro2025
FBR_API_KEY=your-fbr-api-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,gsheir.com
```

### 3. Database Setup

```bash
poetry run python manage.py makemigrations
poetry run python manage.py migrate
poetry run python manage.py createsuperuser
```

### 4. Load Initial Data

Sync teams, players, and matches from FBRef API:

```bash
poetry run python manage.py sync_fbr_data
```

### 5. Run Development Server

```bash
poetry run python manage.py runserver
# Or activate the Poetry shell first:
poetry shell
python manage.py runserver
```

Visit `http://localhost:8000/weuro2025_game/` to access the game.

## Quick Start with Make

If you have `make` installed, you can use these convenient commands:

```bash
# Install dependencies and set up the project
make install

# Run development server
make run

# Set up database
make migrate

# Create sample data
make sample-data

# Format code
make format

# Run tests
make test
```

Run `make help` to see all available commands.

## Game Rules

### How to Play

1. **Join a League**: Create your own league or join one using a league code
2. **Make Selections**: Before each round, select 3 players you think will score
3. **Earn Points**: Get 1 point for each goal scored by your selected players
4. **Compete**: Climb the league table to become champion!

### Selection Process

- **Round 1**: Random selection order
- **Subsequent Rounds**: Lowest-scoring users pick first
- **Provisional Lists**: Build a ranked list of preferred players (max 3x league size)
- **Auto-Selection**: When it's your turn, top 3 available players from your list are selected
- **No Duplicates**: Each player can only be selected once per league per round

### Timing

- **Selection Window**: Opens when current round starts, closes 1 hour before next round
- **Automatic Processing**: Selections confirmed and points calculated automatically
- **Carryover**: Previous round's provisional list carries over if no new selections made

## API Integration

The game integrates with the FBRef API to get real-time football data:

- **Teams**: Tournament participating teams
- **Players**: Player information and statistics
- **Matches**: Fixture list and results
- **Goals**: Goal events for point calculation

### API Commands

```bash
# Full data sync
poetry run python manage.py sync_fbr_data

# Process round logic (selections and points)
poetry run python manage.py process_round

# Process specific round
poetry run python manage.py process_round --round-id 1
```

## Deployment

### Environment Variables

For production deployment, set these environment variables:

```
SECRET_KEY=your-production-secret-key
DEBUG=False
DATABASE_URL=your-production-database-url
FBR_API_KEY=your-fbr-api-key
ALLOWED_HOSTS=your-domain.com
```

### Database Migration

```bash
poetry run python manage.py migrate
poetry run python manage.py collectstatic --noinput
```

### Scheduled Tasks

Set up cron jobs or scheduled tasks for:

```bash
# Sync data every hour
0 * * * * cd /path/to/project && poetry run python manage.py sync_fbr_data

# Process rounds every 10 minutes
*/10 * * * * cd /path/to/project && poetry run python manage.py process_round
```

## Development

### Poetry Commands

```bash
# Install dependencies
poetry install

# Add a new dependency
poetry add <package-name>

# Add a development dependency
poetry add --group dev <package-name>

# Update dependencies
poetry update

# Activate virtual environment
poetry shell

# Run commands in Poetry environment
poetry run <command>

# Show dependency tree
poetry show --tree

# Export requirements.txt (if needed for deployment)
poetry export -f requirements.txt --output requirements.txt
```

### Project Structure

```
gsheir.com/
├── game/                   # Main Django app
│   ├── models.py          # Database models
│   ├── views.py           # View logic
│   ├── urls.py            # URL routing
│   ├── forms.py           # Django forms
│   ├── admin.py           # Admin interface
│   ├── management/        # Custom management commands
│   │   └── commands/
│   │       ├── sync_fbr_data.py
│   │       └── process_round.py
│   └── services/          # External service integrations
│       └── fbr_api.py     # FBRef API service
├── templates/             # HTML templates
│   └── game/
│       ├── base.html      # Base template
│       ├── home.html      # Home page
│       ├── league.html    # League view
│       └── selection.html # Player selection
├── weuro2025/            # Django project settings
├── manage.py             # Django management script
└── requirements.txt      # Python dependencies
```

### Database Models

- **League**: Private leagues with unique codes
- **LeagueParticipant**: User membership in leagues
- **Round**: Tournament rounds with timing
- **Team/Player**: Football teams and players
- **Match/Goal**: Matches and goal events
- **UserSelection**: User's confirmed player selections
- **ProvisionalSelection**: User's ranked preference lists
- **LeagueStanding**: Points and positions per round
- **SelectionOrder**: Pick order for each round

### Key Features

- **Automatic Selection**: Provisional lists enable hands-off participation
- **Fair Ordering**: Lowest scorers pick first (except round 1)
- **Real-time Updates**: API integration keeps data current
- **Responsive Design**: Works on desktop and mobile
- **Admin Interface**: Full admin panel for data management

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions or issues, please open an issue on GitHub or contact the development team.
