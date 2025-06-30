import random

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from game.models import (
    Goal,
    League,
    LeagueStanding,
    ProvisionalSelection,
    Round,
    SelectionOrder,
    UserSelection,
)
from game.services.fbr_api import FBRAPIService


class Command(BaseCommand):
    help = "Process round logic: calculate points and confirm selections"

    def add_arguments(self, parser):
        parser.add_argument(
            "--round-id",
            type=int,
            help="Process specific round by ID",
        )

    def handle(self, *args, **options):
        round_id = options.get("round_id")

        if round_id:
            try:
                round_obj = Round.objects.get(id=round_id)
                self.process_round(round_obj)
            except Round.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"Round with ID {round_id} does not exist")
                )
        else:
            # Process all rounds that need processing
            now = timezone.now()

            # Find rounds that are starting (1 hour before kickoff)
            rounds_starting = Round.objects.filter(
                selection_closes__lte=now, is_active=True, is_completed=False
            )

            for round_obj in rounds_starting:
                self.process_round_selections(round_obj)

            # Find rounds that have ended
            rounds_ended = Round.objects.filter(
                ends_at__lte=now, is_active=True, is_completed=False
            )

            for round_obj in rounds_ended:
                self.process_round_completion(round_obj)

    def process_round(self, round_obj):
        """Process both selections and completion for a specific round"""
        self.process_round_selections(round_obj)
        self.process_round_completion(round_obj)

    def process_round_selections(self, round_obj):
        """Confirm user selections based on their provisional lists"""
        self.stdout.write(f"Processing selections for {round_obj.name}...")

        leagues = League.objects.all()

        for league in leagues:
            self.stdout.write(f"  Processing league: {league.name}")

            # Get or create selection order for this round
            self.ensure_selection_order(league, round_obj)

            # Get selection order for this league/round
            selection_orders = SelectionOrder.objects.filter(
                league=league, round=round_obj
            ).order_by("order")

            # Track selected players in this league
            selected_players = set()

            for selection_order in selection_orders:
                user = selection_order.user

                # Skip if user already has selections for this round
                if UserSelection.objects.filter(
                    user=user, league=league, round=round_obj
                ).exists():
                    continue

                # Get user's provisional selections for this round
                provisional_selections = ProvisionalSelection.objects.filter(
                    user=user, league=league, round=round_obj
                ).order_by("priority")

                # If no provisional selections, try to copy from previous round
                if not provisional_selections.exists():
                    self.copy_previous_round_selections(user, league, round_obj)
                    provisional_selections = ProvisionalSelection.objects.filter(
                        user=user, league=league, round=round_obj
                    ).order_by("priority")

                # Select top 3 available players
                selected_count = 0
                for provisional in provisional_selections:
                    if (
                        provisional.player.id not in selected_players
                        and selected_count < 3
                    ):
                        UserSelection.objects.create(
                            user=user,
                            league=league,
                            round=round_obj,
                            player=provisional.player,
                            selection_order=selected_count + 1,
                        )
                        selected_players.add(provisional.player.id)
                        selected_count += 1

                        self.stdout.write(
                            f"    {user.username} selected {provisional.player.name}"
                        )

                if selected_count < 3:
                    self.stdout.write(
                        f"    Warning: {user.username} only selected {selected_count} players"
                    )

    def process_round_completion(self, round_obj):
        """Calculate points and update standings when round completes"""
        self.stdout.write(f"Processing completion for {round_obj.name}...")

        # Update player goal counts from FBR API
        fbr_service = FBRAPIService()
        fbr_service.update_player_goals(round_obj)

        leagues = League.objects.all()

        for league in leagues:
            self.stdout.write(f"  Calculating points for league: {league.name}")

            # Get all user selections for this round/league
            user_selections = UserSelection.objects.filter(
                league=league, round=round_obj
            ).select_related("user", "player")

            # Group by user
            user_points = {}
            for selection in user_selections:
                if selection.user not in user_points:
                    user_points[selection.user] = 0

                # Count goals scored by this player in this round
                goals_in_round = Goal.objects.filter(
                    player=selection.player, match__round=round_obj
                ).count()

                user_points[selection.user] += goals_in_round

                if goals_in_round > 0:
                    self.stdout.write(
                        f"    {selection.user.username}: {selection.player.name} scored {goals_in_round} goals"
                    )

            # Update or create league standings
            for user, points in user_points.items():
                # Get previous total points
                previous_standing = (
                    LeagueStanding.objects.filter(
                        league=league, user=user, round__number__lt=round_obj.number
                    )
                    .order_by("-round__number")
                    .first()
                )

                previous_total = (
                    previous_standing.total_points if previous_standing else 0
                )
                new_total = previous_total + points

                LeagueStanding.objects.update_or_create(
                    league=league,
                    user=user,
                    round=round_obj,
                    defaults={"points": points, "total_points": new_total},
                )

                self.stdout.write(
                    f"    {user.username}: {points} points this round, {new_total} total"
                )

            # Update positions
            self.update_league_positions(league, round_obj)

        # Mark round as completed
        round_obj.is_completed = True
        round_obj.is_active = False
        round_obj.save()

        self.stdout.write(
            self.style.SUCCESS(f"Round {round_obj.name} processing completed")
        )

    def ensure_selection_order(self, league, round_obj):
        """Ensure selection order exists for this league/round"""
        if SelectionOrder.objects.filter(league=league, round=round_obj).exists():
            return

        participants = league.participants.all()

        if round_obj.number == 1:
            # Random order for first round
            participant_list = list(participants)
            random.shuffle(participant_list)
        else:
            # Order by lowest points first (from previous round)
            previous_round = Round.objects.filter(number=round_obj.number - 1).first()
            if previous_round:
                standings = LeagueStanding.objects.filter(
                    league=league, round=previous_round
                ).order_by(
                    "total_points", "?"
                )  # ? for random tie-breaking

                participant_list = [standing.user for standing in standings]

                # Add any participants who weren't in previous round
                existing_users = set(standing.user for standing in standings)
                for participant in participants:
                    if participant.user not in existing_users:
                        participant_list.append(participant.user)
            else:
                # Fallback to random
                participant_list = [p.user for p in participants]
                random.shuffle(participant_list)

        # Create selection orders
        for i, user in enumerate(participant_list):
            SelectionOrder.objects.create(
                league=league, round=round_obj, user=user, order=i + 1
            )

    def copy_previous_round_selections(self, user, league, round_obj):
        """Copy provisional selections from previous round if none exist"""
        previous_round = Round.objects.filter(number=round_obj.number - 1).first()
        if not previous_round:
            return

        previous_selections = ProvisionalSelection.objects.filter(
            user=user, league=league, round=previous_round
        ).order_by("priority")

        for selection in previous_selections:
            ProvisionalSelection.objects.create(
                user=user,
                league=league,
                round=round_obj,
                player=selection.player,
                priority=selection.priority,
            )

    def update_league_positions(self, league, round_obj):
        """Update positions in league standings"""
        standings = LeagueStanding.objects.filter(
            league=league, round=round_obj
        ).order_by("-total_points", "user__username")

        for i, standing in enumerate(standings):
            standing.position = i + 1
            standing.save()
