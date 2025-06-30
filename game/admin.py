from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.contrib import messages
import json
from django.utils import timezone

from .models import (
    Goal,
    League,
    LeagueParticipant,
    LeagueStanding,
    Match,
    Player,
    ProvisionalSelection,
    Round,
    SelectionOrder,
    Team,
    UserSelection,
)


@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "code",
        "participant_count",
        "max_participants",
        "created_at",
    ]
    list_filter = ["created_at"]
    search_fields = ["name", "code"]
    readonly_fields = ["id", "created_at"]


@admin.register(LeagueParticipant)
class LeagueParticipantAdmin(admin.ModelAdmin):
    list_display = ["user", "league", "joined_at"]
    list_filter = ["league", "joined_at"]
    search_fields = ["user__username", "league__name"]


@admin.register(Round)
class RoundAdmin(admin.ModelAdmin):
    list_display = [
        "number",
        "name",
        "selection_opens",
        "selection_closes",
        "is_active",
        "is_completed",
    ]
    list_filter = ["is_active", "is_completed"]
    ordering = ["number"]


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ["name", "country", "fbr_id"]
    list_filter = ["country"]
    search_fields = ["name", "country"]


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ["name", "team", "position", "goals_scored"]
    list_filter = ["team", "position"]
    search_fields = ["name", "team__name"]
    ordering = ["-goals_scored", "name"]


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ["home_team", "away_team", "round", "kickoff_time", "is_completed", "is_manually_edited"]
    list_filter = ["round", "is_completed", "is_manually_edited", "kickoff_time"]
    search_fields = ["home_team__name", "away_team__name"]
    ordering = ["kickoff_time"]
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('manage-matches/', self.admin_site.admin_view(self.manage_matches_view), name='game_match_manage'),
            path('edit-match/<int:match_id>/', self.admin_site.admin_view(self.edit_match_view), name='game_match_edit'),
            path('input-result/<int:match_id>/', self.admin_site.admin_view(self.input_result_view), name='game_match_result'),
            path('player-data/<int:match_id>/', self.admin_site.admin_view(self.player_data_view), name='game_match_player_data'),
        ]
        return custom_urls + urls
    
    def manage_matches_view(self, request):
        """Custom view for managing matches"""
        rounds = Round.objects.all().prefetch_related('matches__home_team', 'matches__away_team', 'matches__goals__player')
        
        context = {
            'title': 'Manage Matches',
            'rounds': rounds,
            'opts': self.model._meta,
            'has_change_permission': True,
        }
        return render(request, 'admin/game/match/manage_matches.html', context)
    
    def edit_match_view(self, request, match_id):
        """View for editing match details"""
        match = get_object_or_404(Match, id=match_id)
        
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                
                # Update match details
                if 'home_team_id' in data:
                    match.home_team_id = data['home_team_id']
                if 'away_team_id' in data:
                    match.away_team_id = data['away_team_id']
                if 'kickoff_time' in data:
                    match.kickoff_time = timezone.datetime.fromisoformat(data['kickoff_time'].replace('Z', '+00:00'))
                
                match.is_manually_edited = True
                match.save()
                
                return JsonResponse({'success': True, 'message': 'Match updated successfully'})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
        
        teams = Team.objects.all()
        context = {
            'match': match,
            'teams': teams,
        }
        return render(request, 'admin/game/match/edit_match.html', context)
    
    def input_result_view(self, request, match_id):
        """View for inputting match results"""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Input result view called for match_id: {match_id}, method: {request.method}")
        
        match = get_object_or_404(Match, id=match_id)
        
        if request.method == 'POST':
            try:
                logger.info(f"Processing POST request, body: {request.body}")
                data = json.loads(request.body)
                logger.info(f"Parsed JSON data: {data}")
                
                # Clear existing goals
                existing_goals_count = match.goals.all().count()
                logger.info(f"Clearing {existing_goals_count} existing goals")
                match.goals.all().delete()
                
                # Add new goals
                home_goals = 0
                away_goals = 0
                
                goals_data = data.get('goals', [])
                logger.info(f"Processing {len(goals_data)} goals")
                
                for i, goal_data in enumerate(goals_data):
                    logger.info(f"Processing goal {i}: {goal_data}")
                    player = Player.objects.get(id=goal_data['player_id'])
                    logger.info(f"Found player: {player.name} (team: {player.team.name})")
                    
                    goal = Goal.objects.create(
                        match=match,
                        player=player,
                        minute=goal_data['minute'],
                        is_penalty=goal_data.get('is_penalty', False),
                        is_own_goal=goal_data.get('is_own_goal', False)
                    )
                    logger.info(f"Created goal: {goal}")
                    
                    # Count goals for each team
                    if goal_data.get('is_own_goal'):
                        # Own goal counts for the other team
                        if player.team == match.home_team:
                            away_goals += 1
                        else:
                            home_goals += 1
                    else:
                        # Regular goal
                        if player.team == match.home_team:
                            home_goals += 1
                        else:
                            away_goals += 1
                
                logger.info(f"Final score: {match.home_team.name} {home_goals} - {away_goals} {match.away_team.name}")
                
                # Update scores and mark as completed
                match.home_score = home_goals
                match.away_score = away_goals
                match.is_completed = True
                match.is_manually_edited = True
                match.save()
                logger.info(f"Match saved: {match}")
                
                # Update player goal counts
                for player in Player.objects.filter(goals__match=match):
                    old_count = player.goals_scored
                    player.goals_scored = player.goals.filter(is_own_goal=False).count()
                    player.save()
                    logger.info(f"Updated player {player.name} goals from {old_count} to {player.goals_scored}")
                
                logger.info("Successfully updated match result")
                return JsonResponse({'success': True, 'message': 'Match result updated successfully'})
            except Exception as e:
                logger.error(f"Error updating match result: {str(e)}", exc_info=True)
                return JsonResponse({'success': False, 'error': str(e)})
        
        home_players = Player.objects.filter(team=match.home_team)
        away_players = Player.objects.filter(team=match.away_team)
        existing_goals = match.goals.all().select_related('player')
        
        context = {
            'match': match,
            'home_players': home_players,
            'away_players': away_players,
            'existing_goals': existing_goals,
        }
        return render(request, 'admin/game/match/input_result.html', context)
    
    def player_data_view(self, request, match_id):
        """Return player data for a match as JSON"""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Player data view called for match_id: {match_id}")
        
        match = get_object_or_404(Match, id=match_id)
        logger.info(f"Match found: {match.home_team.name} vs {match.away_team.name}")
        
        home_players = Player.objects.filter(team=match.home_team).values('id', 'name')
        away_players = Player.objects.filter(team=match.away_team).values('id', 'name')
        
        home_players_list = list(home_players)
        away_players_list = list(away_players)
        
        logger.info(f"Home players count: {len(home_players_list)}")
        logger.info(f"Away players count: {len(away_players_list)}")
        
        data = {
            'home_team_name': match.home_team.name,
            'away_team_name': match.away_team.name,
            'home_players': home_players_list,
            'away_players': away_players_list,
        }
        
        logger.info(f"Returning data: {data}")
        return JsonResponse(data)


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ["player", "match", "minute", "is_penalty", "is_own_goal"]
    list_filter = ["match__round", "is_penalty", "is_own_goal"]
    search_fields = ["player__name", "match__home_team__name", "match__away_team__name"]
    ordering = ["match", "minute"]


@admin.register(UserSelection)
class UserSelectionAdmin(admin.ModelAdmin):
    list_display = ["user", "league", "round", "player", "selection_order"]
    list_filter = ["league", "round"]
    search_fields = ["user__username", "player__name", "league__name"]
    ordering = ["round", "league", "user", "selection_order"]


@admin.register(ProvisionalSelection)
class ProvisionalSelectionAdmin(admin.ModelAdmin):
    list_display = ["user", "league", "round", "player", "priority"]
    list_filter = ["league", "round"]
    search_fields = ["user__username", "player__name", "league__name"]
    ordering = ["round", "league", "user", "priority"]


@admin.register(LeagueStanding)
class LeagueStandingAdmin(admin.ModelAdmin):
    list_display = ["league", "user", "round", "points", "total_points", "position"]
    list_filter = ["league", "round"]
    search_fields = ["user__username", "league__name"]
    ordering = ["league", "round", "position"]


@admin.register(SelectionOrder)
class SelectionOrderAdmin(admin.ModelAdmin):
    list_display = ["league", "round", "user", "order"]
    list_filter = ["league", "round"]
    search_fields = ["user__username", "league__name"]
    ordering = ["league", "round", "order"]
