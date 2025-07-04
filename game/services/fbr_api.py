import logging
import time

import pandas as pd
import requests

from django.conf import settings

from game.models import Goal, Match, Player, Round, Team

logger = logging.getLogger(__name__)


class FBRAPIService:
    """Service for interacting with FBR API"""

    def __init__(self):
        self.api_key = None
        self.base_url = settings.FBR_API_BASE_URL
        self.generate_api_key()
        self.headers = {"X-API-Key": self.api_key}

        # while not self.check_required_tables():
        #     logger.error("Required tables are missing. Retrying in 10 seconds...")
        #     time.sleep(10)

    # def check_required_tables(self):
    #     """Check if required tables exist in the database"""
    #     required_tables = [
    #         "game_team",
    #         "game_player",
    #         "game_match",
    #         "game_round",
    #         "game_goal",
    #     ]
    #     existing_tables = set(
    #         table.name for table in settings.DATABASES["default"]["OPTIONS"]["tables"]
    #     )
    #     missing_tables = set(required_tables) - existing_tables

    #     if missing_tables:
    #         logger.error(f"Missing required tables: {', '.join(missing_tables)}")
    #         return False
    #     return True

    def generate_api_key(self):
        """Generate a new API key for the FBR API"""
        try:
            url = f"{self.base_url}/generate_api_key"
            response = requests.post(url)
            self.api_key = response.json().get("api_key")
        except requests.RequestException as e:
            logger.error(f"Error generating API key: {e}")

    def get_teams(self, league_id=162):
        """Fetch teams for a given competition"""
        try:
            url = f"{self.base_url}/league-standings"
            params = {"league_id": league_id, "season_id": "2025"}
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            teams = []

            for table in response.json()["data"]:
                for standing in table["standings"]:
                    teams.append(
                        {
                            "team_name": standing["team_name"],
                            "team_id": standing["team_id"],
                        }
                    )
                    logger.info(
                        f"Fetched team: {standing['team_name']} (ID: {standing['team_id']})"
                    )
            return teams

        except requests.RequestException as e:
            logger.error(f"Error fetching teams: {e}")
            return []

    def get_players_on_team(self, team_id):
        """Fetch players for a specific team. The API is faulty so we scrape
        directly from the FBRef website.

        Args:
            team_id (str): The team ID to fetch players for.
        """
        try:
            url = f"https://fbref.com/en/squads/{team_id}/"
            df = pd.read_html(url)
            time.sleep(6)  # Sleep to avoid hitting the server too fast

            players_df = df[0]
            players = []

            for _, row in players_df.iterrows():
                player = {
                    "name": row["Unnamed: 0_level_0"]["Player"],
                    "goals_scored": 0,  # We will calculate tournament goals later
                }
                players.append(player)

            logger.info(f"Fetched {len(players)} players for team ID {team_id}")
            return players

        except Exception as e:
            logger.error(f"Error fetching players for team {team_id}: {e}")
            return []

    def get_matches(self, league_id=162):
        """Fetch matches for a given league"""
        try:
            url = f"{self.base_url}/matches"
            params = {"league_id": league_id, "season_id": "2025"}
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            matches = response.json()["data"]
            logger.info(f"Fetched {len(matches)} matches for league ID {league_id}")
            return matches

        except requests.RequestException as e:
            logger.error(f"Error fetching matches: {e}")
            return []

    def sync_all_data(self, league_id=162):
        """Sync all data from FBR API"""
        logger.info("Starting full data sync from FBR API")

        # Sync teams
        teams = self.get_teams(league_id)
        for team in teams:
            Team.objects.update_or_create(
                name=team["team_name"],
                country=team["team_name"],
                fbr_id=team["team_id"],
            )
            logger.info(f"Synced team: {team['team_name']}")

        for player in settings.WEURO_2025_PLAYERS:
            Player.objects.update_or_create(
                name=player["name"],
                team_id=Team.objects.get(name=player["team"]).id,
                defaults={"goals_scored": 0},  # Initialize goals scored to 0
            )
            logger.info(f"Synced player: {player['name']} for team {player['team']}")

        # Update rounds
        for round_data in settings.WEURO_2025_ROUNDS:
            round_obj, created = Round.objects.update_or_create(
                number=round_data["number"],
                defaults={
                    "name": round_data["name"],
                    "selection_opens": round_data["selection_opens"],
                    "selection_closes": round_data["selection_closes"],
                    "starts_at": round_data["starts_at"],
                    "ends_at": round_data["ends_at"],
                    "is_active": round_data.get("is_active", False),
                    "is_completed": round_data.get("is_completed", False),
                },
            )
            if created:
                logger.info(f"Created new round: {round_obj.name}")
            else:
                logger.info(f"Updated existing round: {round_obj.name}")

        # Sync matches
        matches = settings.WEURO_2025_MATCHES
        for match in matches:
            home_team = Team.objects.get(fbr_id=match["home_team_id"])
            away_team = Team.objects.get(fbr_id=match["away_team_id"])

            # Time in data is in CEST, so we need to convert to UTC
            kickoff_time = f"{match['date']} {match['time']}"
            kickoff_time = (
                pd.to_datetime(kickoff_time)
                .tz_localize(tz="Europe/Berlin")
                .tz_convert(tz="UTC")
            )

            # Round ID is determined from the timestamp
            round_obj = Round.objects.filter(
                starts_at__lte=kickoff_time, ends_at__gte=kickoff_time
            ).first()

            # Skip sync for completed matches and manually edited matches
            if Match.objects.filter(
                home_team=home_team,
                away_team=away_team,
                kickoff_time=kickoff_time,
                round_id=round_obj.id,
                is_completed=True,
                is_manually_edited=True,
            ).exists():
                logger.info(
                    f"Skipping match sync for completed or manually edited match: {home_team.name} vs {away_team.name} at {kickoff_time}"
                )
                continue

            Match.objects.update_or_create(
                home_team=home_team,
                away_team=away_team,
                kickoff_time=kickoff_time,
                round_id=round_obj.id,
                defaults={
                    "is_completed": False,  # Matches are not completed initially
                    "is_manually_edited": False,  # Matches are not manually edited initially
                },
            )
            logger.info(
                f"Synced match: {home_team.name} vs {away_team.name} at {kickoff_time}"
            )

        logger.info("Full data sync completed")
