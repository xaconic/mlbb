from urllib.parse import urlsplit

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Player(models.Model):
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='player_profile',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    player_id = models.BigIntegerField()
    server = models.IntegerField()
    ign = models.CharField(max_length=100)
    main_role = models.CharField(max_length=20)
    highest_rank = models.CharField(max_length=50)
    highest_stars = models.PositiveIntegerField(default=0)
    current_rank = models.CharField(max_length=50)
    current_stars = models.PositiveIntegerField(default=0)
    win_rate = models.DecimalField(max_digits=5, decimal_places=2)
    biography = models.TextField(blank=True, max_length=600)
    preferred_play_style = models.CharField(max_length=80, blank=True)
    available_for_team = models.BooleanField(default=True)
    main_heroes = models.ManyToManyField(
        'Hero',
        through='PlayerHero',
        related_name='players',
        blank=True,
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('ign',)
        constraints = [
            models.UniqueConstraint(
                fields=('player_id', 'server'),
                name='unique_player_id_per_server',
            ),
        ]

    def __str__(self):
        return self.ign


class Hero(models.Model):
    name = models.CharField(max_length=80, unique=True)
    role = models.CharField(max_length=20, blank=True)
    portrait = models.CharField(
        max_length=255,
        blank=True,
        help_text='Optional local static asset path; leave blank to use initials.',
    )
    portrait_url = models.URLField(
        blank=True,
        help_text='Optional Mobile Legends hero portrait URL; leave blank to use the local fallback.',
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        try:
            portrait_host = urlsplit(self.portrait_url).hostname if self.portrait_url else None
        except ValueError:
            portrait_host = None
        if self.portrait_url and portrait_host not in {
            'akmweb.youngjoygame.com',
            'static.wikia.nocookie.net',
        }:
            raise ValidationError({
                'portrait_url': 'Hero portraits must use an approved Mobile Legends artwork source.',
            })


class PlayerHero(models.Model):
    player = models.ForeignKey(Player, related_name='hero_selections', on_delete=models.CASCADE)
    hero = models.ForeignKey(Hero, related_name='player_selections', on_delete=models.PROTECT)
    position = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ('position',)
        constraints = [
            models.UniqueConstraint(fields=('player', 'hero'), name='unique_hero_per_player'),
            models.UniqueConstraint(fields=('player', 'position'), name='unique_hero_position_per_player'),
            models.CheckConstraint(condition=models.Q(position__gte=1, position__lte=5), name='hero_position_between_1_and_5'),
        ]

    def __str__(self):
        return f'{self.player.ign}: {self.hero.name}'


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='community_profile',
        on_delete=models.CASCADE,
    )
    is_player = models.BooleanField(default=True)
    is_team_staff = models.BooleanField(default=False)
    is_tournament_organizer = models.BooleanField(default=False)

    def __str__(self):
        return f'Community roles for {self.user.get_username()}'


class Team(models.Model):
    name = models.CharField(max_length=80, unique=True)
    description = models.TextField(blank=True, max_length=600)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='owned_teams',
        on_delete=models.PROTECT,
    )
    recruiting = models.BooleanField(default=True)
    preferred_role = models.CharField(max_length=20, blank=True)
    minimum_rank = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class TeamRosterEntry(models.Model):
    team = models.ForeignKey(Team, related_name='roster_entries', on_delete=models.CASCADE)
    player = models.ForeignKey(
        Player,
        related_name='team_roster_entries',
        on_delete=models.PROTECT,
    )
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='added_roster_entries',
        on_delete=models.PROTECT,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created_at',)
        constraints = [
            models.UniqueConstraint(fields=('team', 'player'), name='unique_team_roster_player'),
        ]

    def __str__(self):
        return f'{self.player.ign} — {self.team.name}'


class TeamMembership(models.Model):
    class Role(models.TextChoices):
        CAPTAIN = 'captain', 'Captain'
        MANAGER = 'manager', 'Manager'
        COACH = 'coach', 'Coach'
        PLAYER = 'player', 'Player'

    class Status(models.TextChoices):
        REQUESTED = 'requested', 'Requested'
        ACTIVE = 'active', 'Active'
        DECLINED = 'declined', 'Declined'

    team = models.ForeignKey(Team, related_name='memberships', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='team_memberships', on_delete=models.CASCADE)
    role = models.CharField(max_length=12, choices=Role.choices, default=Role.PLAYER)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.REQUESTED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created_at',)
        constraints = [
            models.UniqueConstraint(fields=('team', 'user'), name='unique_team_membership'),
        ]

    def __str__(self):
        return f'{self.user} — {self.team} ({self.status})'


class Tournament(models.Model):
    class Status(models.TextChoices):
        UPCOMING = 'upcoming', 'Upcoming'
        REGISTRATION_CLOSED = 'registration_closed', 'Registration closed'
        COMPLETED = 'completed', 'Completed'

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, max_length=2000)
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='organized_tournaments',
        on_delete=models.PROTECT,
    )
    starts_at = models.DateTimeField()
    registration_deadline = models.DateTimeField()
    format = models.CharField(max_length=60, blank=True)
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.UPCOMING)
    teams = models.ManyToManyField(Team, through='TournamentEntry', related_name='tournaments', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('starts_at', 'name')

    def __str__(self):
        return self.name


class TournamentEntry(models.Model):
    class Status(models.TextChoices):
        REQUESTED = 'requested', 'Requested'
        ACCEPTED = 'accepted', 'Accepted'
        DECLINED = 'declined', 'Declined'

    tournament = models.ForeignKey(Tournament, related_name='entries', on_delete=models.CASCADE)
    team = models.ForeignKey(Team, related_name='tournament_entries', on_delete=models.CASCADE)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.REQUESTED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created_at',)
        constraints = [
            models.UniqueConstraint(fields=('tournament', 'team'), name='unique_tournament_team'),
        ]
