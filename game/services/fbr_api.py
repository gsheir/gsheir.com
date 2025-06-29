import requests
from django.conf import settings
from game.models import Player, Team, Match, Goal, Round
import logging

logger = logging.getLogger(__name__)


class FBRAPIService:
    """Service for interacting with FBR API"""
    
    def __init__(self):
        self.api_key = settings.FBR_API_KEY
        self.base_url = settings.FBR_API_BASE_URL
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def get_competition_data(self, competition_id='womens-euro-2025'):
        """Get competition data from FBR API"""
        try:
            url = f"{self.base_url}/competitions/{competition_id}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching competition data: {e}")
            return None
    
    def get_teams(self, competition_id='womens-euro-2025'):
        """Get teams from FBR API and sync with database"""
        try:
            url = f"{self.base_url}/competitions/{competition_id}/teams"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            teams = []
            for team_data in data.get('teams', []):
                team, created = Team.objects.get_or_create(
                    fbr_id=team_data.get('id'),
                    defaults={
                        'name': team_data.get('name'),
                        'country': team_data.get('country', team_data.get('name'))
                    }
                )
                teams.append(team)
                
                if created:
                    logger.info(f"Created team: {team.name}")
            
            return teams
            
        except requests.RequestException as e:
            logger.error(f"Error fetching teams: {e}")
            return []
    
    def get_players(self, competition_id='womens-euro-2025'):
        """Get players from FBR API and sync with database"""
        try:
            url = f"{self.base_url}/competitions/{competition_id}/players"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            players = []
            for player_data in data.get('players', []):
                # Find team by FBR ID
                team = None
                team_id = player_data.get('team_id')
                if team_id:
                    try:
                        team = Team.objects.get(fbr_id=team_id)
                    except Team.DoesNotExist:
                        logger.warning(f"Team with FBR ID {team_id} not found for player {player_data.get('name')}")
                        continue
                
                if team:
                    player, created = Player.objects.get_or_create(
                        fbr_id=player_data.get('id'),
                        defaults={
                            'name': player_data.get('name'),
                            'team': team,
                            'position': player_data.get('position', 'Unknown')
                        }
                    )
                    players.append(player)
                    
                    if created:
                        logger.info(f"Created player: {player.name}")
            
            return players
            
        except requests.RequestException as e:
            logger.error(f"Error fetching players: {e}")
            return []
    
    def get_matches(self, competition_id='womens-euro-2025'):
        """Get matches from FBR API and sync with database"""
        try:
            url = f"{self.base_url}/competitions/{competition_id}/matches"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            matches = []
            for match_data in data.get('matches', []):
                # Find teams
                home_team = None
                away_team = None
                
                home_team_id = match_data.get('home_team_id')
                away_team_id = match_data.get('away_team_id')
                
                if home_team_id:
                    try:
                        home_team = Team.objects.get(fbr_id=home_team_id)
                    except Team.DoesNotExist:
                        logger.warning(f"Home team with FBR ID {home_team_id} not found")
                        continue
                
                if away_team_id:
                    try:
                        away_team = Team.objects.get(fbr_id=away_team_id)
                    except Team.DoesNotExist:
                        logger.warning(f"Away team with FBR ID {away_team_id} not found")
                        continue
                
                # Find round
                round_number = match_data.get('round', 1)
                round_obj, _ = Round.objects.get_or_create(
                    number=round_number,
                    defaults={
                        'name': f"Round {round_number}",
                        'selection_opens': match_data.get('kickoff_time'),
                        'selection_closes': match_data.get('kickoff_time'),
                        'starts_at': match_data.get('kickoff_time'),
                        'ends_at': match_data.get('kickoff_time')
                    }
                )
                
                if home_team and away_team:
                    match, created = Match.objects.get_or_create(
                        fbr_id=match_data.get('id'),
                        defaults={
                            'round': round_obj,
                            'home_team': home_team,
                            'away_team': away_team,
                            'kickoff_time': match_data.get('kickoff_time'),
                            'home_score': match_data.get('home_score'),
                            'away_score': match_data.get('away_score'),
                            'is_completed': match_data.get('status') == 'completed'
                        }
                    )
                    matches.append(match)
                    
                    if created:
                        logger.info(f"Created match: {match}")
            
            return matches
            
        except requests.RequestException as e:
            logger.error(f"Error fetching matches: {e}")
            return []
    
    def get_match_events(self, match_fbr_id):
        """Get match events (goals) from FBR API"""
        try:
            url = f"{self.base_url}/matches/{match_fbr_id}/events"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            goals = []
            for event in data.get('events', []):
                if event.get('type') == 'goal':
                    # Find match
                    try:
                        match = Match.objects.get(fbr_id=match_fbr_id)
                    except Match.DoesNotExist:
                        logger.warning(f"Match with FBR ID {match_fbr_id} not found")
                        continue
                    
                    # Find player
                    player_fbr_id = event.get('player_id')
                    if player_fbr_id:
                        try:
                            player = Player.objects.get(fbr_id=player_fbr_id)
                        except Player.DoesNotExist:
                            logger.warning(f"Player with FBR ID {player_fbr_id} not found")
                            continue
                        
                        goal, created = Goal.objects.get_or_create(
                            match=match,
                            player=player,
                            minute=event.get('minute', 0),
                            defaults={
                                'is_penalty': event.get('is_penalty', False),
                                'is_own_goal': event.get('is_own_goal', False)
                            }
                        )
                        goals.append(goal)
                        
                        if created:
                            logger.info(f"Created goal: {goal}")
            
            return goals
            
        except requests.RequestException as e:
            logger.error(f"Error fetching match events: {e}")
            return []
    
    def update_player_goals(self, round_obj):
        """Update player goal counts for a specific round"""
        matches = Match.objects.filter(round=round_obj)
        
        for match in matches:
            if match.fbr_id:
                self.get_match_events(match.fbr_id)
        
        # Update player goal counts
        for player in Player.objects.all():
            goal_count = Goal.objects.filter(player=player).count()
            if player.goals_scored != goal_count:
                player.goals_scored = goal_count
                player.save()
                logger.info(f"Updated {player.name} goal count to {goal_count}")
    
    def sync_all_data(self, competition_id='womens-euro-2025'):
        """Sync all data from FBR API"""
        logger.info("Starting full data sync from FBR API")
        
        # Sync teams first
        teams = self.get_teams(competition_id)
        logger.info(f"Synced {len(teams)} teams")
        
        # Sync players
        players = self.get_players(competition_id)
        logger.info(f"Synced {len(players)} players")
        
        # Sync matches
        matches = self.get_matches(competition_id)
        logger.info(f"Synced {len(matches)} matches")
        
        # Sync goals for all matches
        for match in matches:
            if match.fbr_id:
                goals = self.get_match_events(match.fbr_id)
                logger.info(f"Synced {len(goals)} goals for {match}")
        
        # Update player goal counts
        for player in Player.objects.all():
            goal_count = Goal.objects.filter(player=player).count()
            if player.goals_scored != goal_count:
                player.goals_scored = goal_count
                player.save()
        
        logger.info("Full data sync completed")
