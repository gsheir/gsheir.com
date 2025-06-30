import uuid

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class League(models.Model):
    """A league where users compete"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_leagues"
    )
    max_participants = models.IntegerField(
        default=10, validators=[MinValueValidator(2), MaxValueValidator(20)]
    )

    def __str__(self):
        return self.name

    @property
    def participant_count(self):
        return self.participants.count()


class LeagueParticipant(models.Model):
    """Users participating in a league"""

    league = models.ForeignKey(
        League, on_delete=models.CASCADE, related_name="participants"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="league_participations"
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("league", "user")

    def __str__(self):
        return f"{self.user.username} in {self.league.name}"


class Round(models.Model):
    """Tournament rounds"""

    number = models.IntegerField()
    name = models.CharField(max_length=100)
    selection_opens = models.DateTimeField()
    selection_closes = models.DateTimeField()
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    is_active = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)

    class Meta:
        ordering = ["number"]

    def __str__(self):
        return f"Round {self.number}: {self.name}"

    @property
    def is_selection_open(self):
        """Check if the selection window is currently open for this round"""
        from django.utils import timezone

        now = timezone.now()
        return self.selection_opens <= now <= self.selection_closes

    @property
    def is_in_progress(self):
        """Check if this round is currently in progress (matches happening)"""
        from django.utils import timezone

        now = timezone.now()
        return self.starts_at <= now <= self.ends_at and not self.is_completed

    @classmethod
    def get_current_round(cls):
        """Get the round that is currently in progress"""
        from django.utils import timezone

        now = timezone.now()
        return cls.objects.filter(
            starts_at__lte=now, ends_at__gte=now, is_completed=False
        ).first()

    @classmethod
    def get_selection_round(cls):
        """Get the round that is currently open for selections"""
        from django.utils import timezone

        now = timezone.now()
        return cls.objects.filter(
            selection_opens__lte=now, selection_closes__gte=now
        ).first()

    @classmethod
    def get_next_round(cls):
        """Get the next upcoming round"""
        from django.utils import timezone

        now = timezone.now()
        return (
            cls.objects.filter(starts_at__gt=now, is_completed=False)
            .order_by("starts_at")
            .first()
        )


class Team(models.Model):
    """Football teams"""

    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    fbr_id = models.CharField(max_length=50, unique=True, null=True, blank=True)

    def __str__(self):
        return self.name


class Player(models.Model):
    """Football players"""

    name = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="players")
    position = models.CharField(max_length=50)
    fbr_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    goals_scored = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.team.name})"

    class Meta:
        ordering = ["-goals_scored", "name"]


class Match(models.Model):
    """Tournament matches"""

    round = models.ForeignKey(Round, on_delete=models.CASCADE, related_name="matches")
    home_team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="home_matches"
    )
    away_team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="away_matches"
    )
    kickoff_time = models.DateTimeField()
    home_score = models.IntegerField(null=True, blank=True)
    away_score = models.IntegerField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    fbr_id = models.CharField(max_length=50, unique=True, null=True, blank=True)

    def __str__(self):
        return f"{self.home_team.name} vs {self.away_team.name}"

    class Meta:
        ordering = ["kickoff_time"]


class Goal(models.Model):
    """Goals scored in matches"""

    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="goals")
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="goals")
    minute = models.IntegerField()
    is_penalty = models.BooleanField(default=False)
    is_own_goal = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.player.name} - {self.minute}'"

    class Meta:
        ordering = ["match", "minute"]


class UserSelection(models.Model):
    """User's player selections for a round"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="selections")
    league = models.ForeignKey(
        League, on_delete=models.CASCADE, related_name="selections"
    )
    round = models.ForeignKey(
        Round, on_delete=models.CASCADE, related_name="selections"
    )
    player = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="user_selections"
    )
    selection_order = (
        models.IntegerField()
    )  # Order in which player was selected (1, 2, or 3)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "league", "round", "selection_order")
        ordering = ["round", "user", "selection_order"]

    def __str__(self):
        return f"{self.user.username} - {self.player.name} (Round {self.round.number})"


class ProvisionalSelection(models.Model):
    """User's provisional selection list for a round"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="provisional_selections"
    )
    league = models.ForeignKey(
        League, on_delete=models.CASCADE, related_name="provisional_selections"
    )
    round = models.ForeignKey(
        Round, on_delete=models.CASCADE, related_name="provisional_selections"
    )
    player = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="provisional_selections"
    )
    priority = models.IntegerField()  # Priority order (1 = highest priority)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "league", "round", "player")
        ordering = ["round", "user", "priority"]

    def __str__(self):
        return f"{self.user.username} provisional: {self.player.name} (Priority {self.priority})"


class LeagueStanding(models.Model):
    """League standings for each round"""

    league = models.ForeignKey(
        League, on_delete=models.CASCADE, related_name="standings"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="standings")
    round = models.ForeignKey(Round, on_delete=models.CASCADE, related_name="standings")
    points = models.IntegerField(default=0)
    total_points = models.IntegerField(default=0)  # Cumulative points
    position = models.IntegerField(default=1)

    class Meta:
        unique_together = ("league", "user", "round")
        ordering = ["league", "round", "-total_points", "user__username"]

    def __str__(self):
        return f"{self.league.name} - {self.user.username}: {self.total_points} pts"


class SelectionOrder(models.Model):
    """Selection order for each round in each league"""

    league = models.ForeignKey(
        League, on_delete=models.CASCADE, related_name="selection_orders"
    )
    round = models.ForeignKey(
        Round, on_delete=models.CASCADE, related_name="selection_orders"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="selection_orders"
    )
    order = models.IntegerField()  # 1 = picks first, etc.

    class Meta:
        unique_together = ("league", "round", "user")
        ordering = ["league", "round", "order"]

    def __str__(self):
        return f"{self.league.name} - Round {self.round.number}: {self.user.username} picks {self.order}"
