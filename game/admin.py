from django.contrib import admin
from .models import (
    League, LeagueParticipant, Round, Team, Player, Match, Goal,
    UserSelection, ProvisionalSelection, LeagueStanding, SelectionOrder
)


@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'participant_count', 'max_participants', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'code']
    readonly_fields = ['id', 'created_at']


@admin.register(LeagueParticipant)
class LeagueParticipantAdmin(admin.ModelAdmin):
    list_display = ['user', 'league', 'joined_at']
    list_filter = ['league', 'joined_at']
    search_fields = ['user__username', 'league__name']


@admin.register(Round)
class RoundAdmin(admin.ModelAdmin):
    list_display = ['number', 'name', 'selection_opens', 'selection_closes', 'is_active', 'is_completed']
    list_filter = ['is_active', 'is_completed']
    ordering = ['number']


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'fbr_id']
    list_filter = ['country']
    search_fields = ['name', 'country']


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['name', 'team', 'position', 'goals_scored']
    list_filter = ['team', 'position']
    search_fields = ['name', 'team__name']
    ordering = ['-goals_scored', 'name']


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['home_team', 'away_team', 'round', 'kickoff_time', 'is_completed']
    list_filter = ['round', 'is_completed', 'kickoff_time']
    search_fields = ['home_team__name', 'away_team__name']
    ordering = ['kickoff_time']


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ['player', 'match', 'minute', 'is_penalty', 'is_own_goal']
    list_filter = ['match__round', 'is_penalty', 'is_own_goal']
    search_fields = ['player__name', 'match__home_team__name', 'match__away_team__name']
    ordering = ['match', 'minute']


@admin.register(UserSelection)
class UserSelectionAdmin(admin.ModelAdmin):
    list_display = ['user', 'league', 'round', 'player', 'selection_order']
    list_filter = ['league', 'round']
    search_fields = ['user__username', 'player__name', 'league__name']
    ordering = ['round', 'league', 'user', 'selection_order']


@admin.register(ProvisionalSelection)
class ProvisionalSelectionAdmin(admin.ModelAdmin):
    list_display = ['user', 'league', 'round', 'player', 'priority']
    list_filter = ['league', 'round']
    search_fields = ['user__username', 'player__name', 'league__name']
    ordering = ['round', 'league', 'user', 'priority']


@admin.register(LeagueStanding)
class LeagueStandingAdmin(admin.ModelAdmin):
    list_display = ['league', 'user', 'round', 'points', 'total_points', 'position']
    list_filter = ['league', 'round']
    search_fields = ['user__username', 'league__name']
    ordering = ['league', 'round', 'position']


@admin.register(SelectionOrder)
class SelectionOrderAdmin(admin.ModelAdmin):
    list_display = ['league', 'round', 'user', 'order']
    list_filter = ['league', 'round']
    search_fields = ['user__username', 'league__name']
    ordering = ['league', 'round', 'order']
