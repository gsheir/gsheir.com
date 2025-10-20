import json
import random
import string

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Count, Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, TemplateView

from .forms import JoinLeagueForm, LeagueForm
from .models import (
    Goal,
    League,
    LeagueParticipant,
    LeagueStanding,
    Player,
    ProvisionalSelection,
    Round,
    SelectionOrder,
    UserSelection,
)


class HomeView(TemplateView):
    template_name = "home.html"


class AboutMeView(TemplateView):
    template_name = "about_me/home.html"


class BlogHomeView(TemplateView):
    template_name = "blog/home.html"


class BlogFantasyFootballView(TemplateView):
    template_name = "blog/fantasy_football.html"


class BlogCoachingView(TemplateView):
    template_name = "blog/coaching.html"


class BlogArsenalPressPart1View(TemplateView):
    template_name = "blog/arsenal_press_part_1.html"


class BlogArsenalPressPart2View(TemplateView):
    template_name = "blog/arsenal_press_part_2.html"

class BlogArsenalCornersPart1View(TemplateView):
    template_name = "blog/arsenal_corners_part_1.html"
    
class BlogArsenalCornersPart2View(TemplateView):
    template_name = "blog/arsenal_corners_part_2.html"


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = "game/register.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response

    def get_success_url(self):
        return "/weuro2025_game/"


class GameHomeView(LoginRequiredMixin, TemplateView):
    template_name = "game/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_leagues = LeagueParticipant.objects.filter(
            user=self.request.user
        ).select_related("league")
        context["user_leagues"] = user_leagues

        # Get current round and selection round
        current_round = Round.get_current_round()
        selection_round = Round.get_selection_round()
        context["current_round"] = current_round
        context["selection_round"] = selection_round

        return context


class CreateLeagueView(LoginRequiredMixin, CreateView):
    form_class = LeagueForm
    template_name = "game/create_league.html"

    def form_valid(self, form):
        # Generate unique league code
        while True:
            code = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if not League.objects.filter(code=code).exists():
                break

        form.instance.code = code
        form.instance.created_by = self.request.user
        response = super().form_valid(form)

        # Add creator as first participant
        LeagueParticipant.objects.create(league=self.object, user=self.request.user)

        messages.success(
            self.request, f"League created successfully! League code: {code}"
        )
        return response

    def get_success_url(self):
        return f"/weuro2025_game/league/{self.object.id}/"


class JoinLeagueView(LoginRequiredMixin, View):
    template_name = "game/join_league.html"

    def get(self, request):
        form = JoinLeagueForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = JoinLeagueForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"]
            try:
                league = League.objects.get(code=code)

                # Check if user is already in league
                if LeagueParticipant.objects.filter(
                    league=league, user=request.user
                ).exists():
                    messages.error(request, "You are already in this league.")
                    return render(request, self.template_name, {"form": form})

                # Check if league is full
                if league.participant_count >= league.max_participants:
                    messages.error(request, "This league is full.")
                    return render(request, self.template_name, {"form": form})

                # Add user to league
                LeagueParticipant.objects.create(league=league, user=request.user)
                messages.success(request, f"Successfully joined {league.name}!")
                return redirect("game:league", league_id=league.id)

            except League.DoesNotExist:
                messages.error(request, "Invalid league code.")

        return render(request, self.template_name, {"form": form})


class LeagueView(LoginRequiredMixin, TemplateView):
    template_name = "game/league.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        league_id = kwargs["league_id"]
        league = get_object_or_404(League, id=league_id)

        # Check if user is in league
        if not LeagueParticipant.objects.filter(
            league=league, user=self.request.user
        ).exists():
            messages.error(self.request, "You are not a member of this league.")
            return context

        context["league"] = league

        # Get current round (in progress) and selection round (open for selections)
        current_round = Round.get_current_round()
        selection_round = Round.get_selection_round()
        next_round = Round.get_next_round()

        context["current_round"] = current_round
        context["selection_round"] = selection_round
        context["next_round"] = next_round

        # Get matches for current round (if any)
        if current_round:
            current_matches = (
                current_round.matches.all()
                .select_related("home_team", "away_team")
                .order_by("kickoff_time")
            )
            context["current_matches"] = current_matches

        # Get matches for next round (if any)
        if next_round:
            next_matches = (
                next_round.matches.all()
                .select_related("home_team", "away_team")
                .order_by("kickoff_time")
            )
            context["next_matches"] = next_matches

        # For standings and selections, use the most recent completed round or current round
        standings_round = (
            current_round
            or Round.objects.filter(is_completed=True).order_by("-number").first()
        )
        if standings_round:
            # Get league standings for the round
            standings = (
                LeagueStanding.objects.filter(league=league, round=standings_round)
                .select_related("user")
                .order_by("-total_points", "user__username")
            )
            context["standings"] = standings

            # Get user selections for the round
            selections = (
                UserSelection.objects.filter(league=league, round=standings_round)
                .select_related("user", "player")
                .order_by("user__username", "selection_order")
            )

            # Group selections by user
            user_selections = {}
            for selection in selections:
                if selection.user not in user_selections:
                    user_selections[selection.user] = []
                user_selections[selection.user].append(selection.player)

            context["user_selections"] = user_selections

        return context


class SelectionView(LoginRequiredMixin, TemplateView):
    template_name = "game/selection.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        league_id = kwargs["league_id"]
        league = get_object_or_404(League, id=league_id)

        # Check if user is in league
        if not LeagueParticipant.objects.filter(
            league=league, user=self.request.user
        ).exists():
            messages.error(self.request, "You are not a member of this league.")
            return context

        context["league"] = league

        # Get the round that's open for selection
        selection_round = Round.get_selection_round()
        if not selection_round:
            messages.error(self.request, "No round is currently open for selections.")
            return context

        context["current_round"] = selection_round

        # Check if selection is still open
        selection_open = selection_round.is_selection_open
        context["selection_open"] = selection_open

        # Get all players
        players = (
            Player.objects.all()
            .select_related("team")
            .order_by("-goals_scored", "name")
        )
        context["players"] = players

        # Get user's provisional selections
        provisional_selections = (
            ProvisionalSelection.objects.filter(
                user=self.request.user, league=league, round=selection_round
            )
            .select_related("player")
            .order_by("priority")
        )
        context["provisional_selections"] = provisional_selections

        # Get already selected players in this league/round (by all users)
        selected_players = UserSelection.objects.filter(
            league=league, round=selection_round
        ).values_list("player_id", flat=True)
        context["selected_players"] = list(selected_players)

        return context


class PlayerListAPIView(LoginRequiredMixin, View):
    def get(self, request):
        players = (
            Player.objects.all()
            .select_related("team")
            .values("id", "name", "team__name", "position", "goals_scored")
            .order_by("-goals_scored", "name")
        )

        return JsonResponse({"players": list(players)})


class ProvisionalSelectionAPIView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            league_id = data.get("league_id")
            round_id = data.get("round_id")
            player_ids = data.get("player_ids", [])

            league = get_object_or_404(League, id=league_id)
            selection_round = get_object_or_404(Round, id=round_id)

            # Check if user is in league
            if not LeagueParticipant.objects.filter(
                league=league, user=request.user
            ).exists():
                return JsonResponse({"error": "Not authorized"}, status=403)

            # Check if selection is still open
            if not selection_round.is_selection_open:
                return JsonResponse({"error": "Selection window is closed"}, status=400)

            # Clear existing provisional selections
            ProvisionalSelection.objects.filter(
                user=request.user, league=league, round=selection_round
            ).delete()

            # Create new provisional selections
            max_selections = league.participant_count * 3
            for i, player_id in enumerate(player_ids[:max_selections]):
                try:
                    player = Player.objects.get(id=player_id)
                    ProvisionalSelection.objects.create(
                        user=request.user,
                        league=league,
                        round=selection_round,
                        player=player,
                        priority=i + 1,
                    )
                except Player.DoesNotExist:
                    continue

            return JsonResponse({"success": True})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    def get(self, request):
        league_id = request.GET.get("league_id")
        round_id = request.GET.get("round_id")

        if not league_id or not round_id:
            return JsonResponse({"error": "Missing parameters"}, status=400)

        provisional_selections = (
            ProvisionalSelection.objects.filter(
                user=request.user, league_id=league_id, round_id=round_id
            )
            .select_related("player", "player__team")
            .order_by("priority")
        )

        selections_data = [
            {
                "id": ps.player.id,
                "name": ps.player.name,
                "team": ps.player.team.name,
                "position": ps.player.position,
                "goals_scored": ps.player.goals_scored,
                "priority": ps.priority,
            }
            for ps in provisional_selections
        ]

        return JsonResponse({"provisional_selections": selections_data})
