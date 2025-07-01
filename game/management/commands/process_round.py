import random

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from game.models import (
    Goal,
    League,
    LeagueStanding,
    Match,
    Player,
    ProvisionalSelection,
    Round,
    SelectionOrder,
    UserSelection,
)


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
            # Update round statuses first
            self.update_round_statuses()

            # Update points for any newly completed matches
            self.update_points_for_completed_matches()

            # Process rounds that need selection processing
            self.process_selection_rounds()

            # Process rounds that need completion processing
            self.process_completion_rounds()

    def update_round_statuses(self):
        """Update round statuses based on current time"""
        now = timezone.now()

        # Close selection for rounds where selection window has ended
        rounds_to_close = Round.objects.filter(
            selection_closes__lte=now, is_active=True
        )

        for round_obj in rounds_to_close:
            if round_obj.selection_closes <= now:
                self.stdout.write(f"Closing selection for {round_obj.name}")
                # Don't mark as inactive yet - wait for round to actually end

        # Open selection for rounds where selection window has started
        rounds_to_open = Round.objects.filter(
            selection_opens__lte=now,
            selection_closes__gt=now,
            is_active=False,
            is_completed=False,
        )

        for round_obj in rounds_to_open:
            round_obj.is_active = True
            round_obj.save()
            self.stdout.write(f"Opened selection for {round_obj.name}")

    def process_selection_rounds(self):
        """Process selection confirmation for rounds where selection has closed"""
        now = timezone.now()

        rounds_for_selection = Round.objects.filter(
            selection_closes__lte=now, is_active=True, is_completed=False
        )

        for round_obj in rounds_for_selection:
            self.process_round_selections(round_obj)

    def process_completion_rounds(self):
        """Process completion for rounds that have ended"""
        now = timezone.now()

        rounds_for_completion = Round.objects.filter(
            ends_at__lte=now, is_active=True, is_completed=False
        )

        for round_obj in rounds_for_completion:
            # Check if all matches in the round are completed
            incomplete_matches = Match.objects.filter(
                round=round_obj, is_completed=False
            ).count()

            if incomplete_matches == 0:
                self.process_round_completion(round_obj)
            else:
                self.stdout.write(
                    f"Round {round_obj.name} has {incomplete_matches} incomplete matches - skipping completion"
                )

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

        # Update player goal counts from manually entered goals
        self.update_player_goals_from_matches(round_obj)

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

                # Count goals scored by this player in this round (excluding own goals)
                goals_in_round = Goal.objects.filter(
                    player=selection.player,
                    match__round=round_obj,
                    is_own_goal=False,  # Don't count own goals for the player
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

        # Mark round as completed and inactive
        round_obj.is_completed = True
        round_obj.is_active = False
        round_obj.save()

        self.stdout.write(
            self.style.SUCCESS(f"Round {round_obj.name} processing completed")
        )

    def update_player_goals_from_matches(self, round_obj):
        """Update player goal counts from manually entered match results"""
        self.stdout.write(f"  Updating player goal counts from matches...")

        # Get all players who scored in this round
        players_with_goals = Player.objects.filter(
            goals__match__round=round_obj
        ).distinct()

        for player in players_with_goals:
            # Count total goals (excluding own goals) for this player
            total_goals = Goal.objects.filter(player=player, is_own_goal=False).count()

            if player.goals_scored != total_goals:
                player.goals_scored = total_goals
                player.save()
                self.stdout.write(
                    f"    Updated {player.name}: {total_goals} total goals"
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
            participant_users = [p.user for p in participant_list]
        else:
            # Order by lowest total points first (from previous round)
            previous_round = Round.objects.filter(number=round_obj.number - 1).first()
            if previous_round:
                # Get standings from the previous round
                standings = LeagueStanding.objects.filter(
                    league=league, round=previous_round
                ).order_by(
                    "total_points"
                )  # Lowest points first

                # If there are ties, we need to randomize within each tie group
                standings_list = list(standings)

                # Group by total points for tie-breaking
                points_groups = {}
                for standing in standings_list:
                    points = standing.total_points
                    if points not in points_groups:
                        points_groups[points] = []
                    points_groups[points].append(standing.user)

                # Build final order with random tie-breaking
                participant_users = []
                for points in sorted(points_groups.keys()):  # Lowest to highest
                    tied_users = points_groups[points]
                    random.shuffle(tied_users)  # Random tie-breaker
                    participant_users.extend(tied_users)

                # Add any participants who weren't in previous round
                existing_users = set(participant_users)
                for participant in participants:
                    if participant.user not in existing_users:
                        participant_users.append(participant.user)
            else:
                # Fallback to random if no previous round found
                participant_list = [p.user for p in participants]
                random.shuffle(participant_list)
                participant_users = participant_list

        # Create selection orders
        for i, user in enumerate(participant_users):
            SelectionOrder.objects.create(
                league=league, round=round_obj, user=user, order=i + 1
            )

        self.stdout.write(
            f"    Created selection order for {len(participant_users)} users in {league.name}"
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

    def update_points_for_completed_matches(self):
        """Update points for matches that have been completed since last run"""
        self.stdout.write("Checking for newly completed matches...")

        # Find rounds that are active but not completed
        active_rounds = Round.objects.filter(is_active=True, is_completed=False)

        for round_obj in active_rounds:
            # Check if there are completed matches in this round
            completed_matches = Match.objects.filter(round=round_obj, is_completed=True)

            if completed_matches.exists():
                self.stdout.write(
                    f"Updating points for completed matches in {round_obj.name}"
                )

                # Update player goal counts
                self.update_player_goals_from_matches(round_obj)

                # Recalculate points for all leagues
                leagues = League.objects.all()

                for league in leagues:
                    # Get all user selections for this round/league
                    user_selections = UserSelection.objects.filter(
                        league=league, round=round_obj
                    ).select_related("user", "player")

                    if not user_selections.exists():
                        continue  # Skip if no selections made yet

                    # Recalculate points for this round
                    user_points = {}
                    for selection in user_selections:
                        if selection.user not in user_points:
                            user_points[selection.user] = 0

                        # Count goals scored by this player in this round (excluding own goals)
                        goals_in_round = Goal.objects.filter(
                            player=selection.player,
                            match__round=round_obj,
                            is_own_goal=False,
                        ).count()

                        user_points[selection.user] += goals_in_round

                    # Update league standings for this round
                    for user, points in user_points.items():
                        # Get previous total points from earlier rounds
                        previous_total = 0
                        if round_obj.number > 1:
                            previous_standing = (
                                LeagueStanding.objects.filter(
                                    league=league,
                                    user=user,
                                    round__number__lt=round_obj.number,
                                )
                                .order_by("-round__number")
                                .first()
                            )
                            if previous_standing:
                                previous_total = previous_standing.total_points

                        new_total = previous_total + points

                        LeagueStanding.objects.update_or_create(
                            league=league,
                            user=user,
                            round=round_obj,
                            defaults={"points": points, "total_points": new_total},
                        )

                    # Update positions
                    self.update_league_positions(league, round_obj)
