from django import forms
from django.db import transaction
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Hero, Player, PlayerHero, Team, TeamMembership, Tournament, UserProfile


ROLES = (
    ('Gold Lane', 'Gold Lane'),
    ('Exp Lane', 'Exp Lane'),
    ('Mid Lane', 'Mid Lane'),
    ('Jungle', 'Jungle'),
    ('Roam', 'Roam'),
)

RANK_GROUPS = (
    ('Warrior', (('Warrior III', 'Warrior III'), ('Warrior II', 'Warrior II'), ('Warrior I', 'Warrior I'))),
    ('Elite', (('Elite III', 'Elite III'), ('Elite II', 'Elite II'), ('Elite I', 'Elite I'))),
    ('Master', (('Master IV', 'Master IV'), ('Master III', 'Master III'), ('Master II', 'Master II'), ('Master I', 'Master I'))),
    ('Grandmaster', (('Grandmaster V', 'Grandmaster V'), ('Grandmaster IV', 'Grandmaster IV'), ('Grandmaster III', 'Grandmaster III'), ('Grandmaster II', 'Grandmaster II'), ('Grandmaster I', 'Grandmaster I'))),
    ('Epic', (('Epic V', 'Epic V'), ('Epic IV', 'Epic IV'), ('Epic III', 'Epic III'), ('Epic II', 'Epic II'), ('Epic I', 'Epic I'))),
    ('Legend', (('Legend V', 'Legend V'), ('Legend IV', 'Legend IV'), ('Legend III', 'Legend III'), ('Legend II', 'Legend II'), ('Legend I', 'Legend I'))),
    ('Mythic', (
        ('Mythic', 'Mythic'),
        ('Mythical Honor', 'Mythical Honor'),
        ('Mythical Glory', 'Mythical Glory'),
        ('Mythical Immortal', 'Mythical Immortal'),
    )),
)
RANK_VALUES = tuple(rank for _, group in RANK_GROUPS for rank, _ in group)
MYTHIC_STAR_RANGES = {
    'Mythic': (1, 24),
    'Mythical Honor': (25, 49),
    'Mythical Glory': (50, 99),
    'Mythical Immortal': (100, None),
}


class PlayerForm(forms.ModelForm):
    main_role = forms.ChoiceField(choices=ROLES)
    highest_rank = forms.ChoiceField(choices=RANK_GROUPS)
    current_rank = forms.ChoiceField(choices=RANK_GROUPS)
    highest_stars = forms.IntegerField(min_value=0, widget=forms.NumberInput(attrs={'min': 0, 'step': 1}))
    current_stars = forms.IntegerField(min_value=0, widget=forms.NumberInput(attrs={'min': 0, 'step': 1}))
    win_rate = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        min_value=0,
        max_value=100,
        widget=forms.NumberInput(attrs={'min': 0, 'max': 100, 'step': '0.01'}),
    )

    class Meta:
        model = Player
        fields = (
            'player_id',
            'server',
            'ign',
            'main_role',
            'highest_rank',
            'highest_stars',
            'current_rank',
            'current_stars',
            'win_rate',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['player_id'].widget.attrs.update({'step': 1})
        self.fields['server'].widget.attrs.update({'step': 1})
        self.fields['ign'].widget.attrs.update({'maxlength': 100})

    def clean_highest_stars(self):
        return self._validate_rank_stars('highest_rank', 'highest_stars')

    def clean_current_stars(self):
        return self._validate_rank_stars('current_rank', 'current_stars')

    def _validate_rank_stars(self, rank_field, stars_field):
        stars = self.cleaned_data[stars_field]
        rank = self.cleaned_data.get(rank_field)
        star_range = MYTHIC_STAR_RANGES.get(rank)
        if star_range is None:
            return stars

        minimum, maximum = star_range
        if stars < minimum or (maximum is not None and stars > maximum):
            if maximum is None:
                message = f'{rank} requires at least {minimum} stars.'
            else:
                message = f'{rank} requires {minimum}-{maximum} stars.'
            raise forms.ValidationError(message)
        return stars


class StyledAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'autocomplete': 'username',
            'placeholder': 'Enter your username or email',
            'autofocus': True,
        })
        self.fields['username'].label = 'Username or email'
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'autocomplete': 'current-password',
            'placeholder': 'Enter your password',
        })
        self.fields['password'].label = 'Password'

    def clean(self):
        """Allow the sign-in field to accept either username or account email."""
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if username and password:
            login_identifier = username
            if '@' in username:
                user = get_user_model().objects.filter(email__iexact=username).only('username').first()
                if user:
                    login_identifier = user.get_username()
            self.user_cache = authenticate(
                self.request,
                username=login_identifier,
                password=password,
            )
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'autocomplete': 'email',
            'placeholder': 'you@example.com',
        }),
    )
    roles = forms.MultipleChoiceField(
        choices=(
            ('player', 'Player looking for a team'),
            ('staff', 'Captain, manager, or coach'),
            ('organizer', 'Tournament organizer'),
        ),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        error_messages={'required': 'Choose at least one way you will use the platform.'},
    )

    class Meta:
        model = get_user_model()
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'autocomplete': 'username',
            'placeholder': 'Choose a username',
            'autofocus': True,
        })
        self.fields['username'].label = 'Username'
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'autocomplete': 'new-password',
            'placeholder': 'Create a password',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'autocomplete': 'new-password',
            'placeholder': 'Confirm your password',
        })
        self.fields['email'].label = 'Email address'
        self.fields['password1'].label = 'Create a password'
        self.fields['password2'].label = 'Confirm your password'

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            roles = self.cleaned_data['roles']
            UserProfile.objects.create(
                user=user,
                is_player='player' in roles,
                is_team_staff='staff' in roles,
                is_tournament_organizer='organizer' in roles,
            )
        return user

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if get_user_model().objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email address already exists.')
        return email


class PlayerProfileForm(forms.ModelForm):
    main_role = forms.ChoiceField(choices=ROLES)
    highest_rank = forms.ChoiceField(choices=RANK_GROUPS)
    current_rank = forms.ChoiceField(choices=RANK_GROUPS)
    highest_stars = forms.IntegerField(min_value=0)
    current_stars = forms.IntegerField(min_value=0)
    win_rate = forms.DecimalField(max_digits=5, decimal_places=2, min_value=0, max_value=100)
    main_heroes = forms.ModelMultipleChoiceField(
        queryset=Hero.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        error_messages={'required': 'Select exactly five main heroes.'},
    )

    class Meta:
        model = Player
        fields = (
            'player_id', 'server', 'ign', 'main_role',
            'highest_rank', 'highest_stars', 'current_rank', 'current_stars',
            'win_rate', 'preferred_play_style', 'biography', 'available_for_team',
        )
        widgets = {
            'biography': forms.Textarea(attrs={'rows': 4, 'maxlength': 600}),
            'available_for_team': forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs['class'] = 'form-control'
        self.fields['main_heroes'].queryset = Hero.objects.filter(is_active=True)
        self.fields['main_heroes'].widget.attrs['class'] = 'hero-choice'
        self.fields['highest_stars'].min_value = 0
        self.fields['current_stars'].min_value = 0
        self.fields['win_rate'].min_value = 0
        self.fields['win_rate'].max_value = 100
        if self.instance.pk:
            self.initial['main_heroes'] = self.instance.main_heroes.all()

    def clean_main_heroes(self):
        heroes = self.cleaned_data['main_heroes']
        if len(heroes) != 5:
            raise forms.ValidationError('Choose exactly five distinct main heroes.')
        return heroes

    def clean_highest_stars(self):
        return PlayerForm._validate_rank_stars(self, 'highest_rank', 'highest_stars')

    def clean_current_stars(self):
        return PlayerForm._validate_rank_stars(self, 'current_rank', 'current_stars')

    @transaction.atomic
    def save(self, commit=True):
        player = super().save(commit=commit)
        if commit:
            PlayerHero.objects.filter(player=player).delete()
            PlayerHero.objects.bulk_create([
                PlayerHero(player=player, hero=hero, position=index)
                for index, hero in enumerate(self.cleaned_data['main_heroes'], start=1)
            ])
        return player


class TeamForm(forms.ModelForm):
    preferred_role = forms.ChoiceField(
        choices=(('', 'Any role'),) + ROLES,
        required=False,
    )
    minimum_rank = forms.ChoiceField(
        choices=(('', 'Any rank'),) + tuple((value, value) for value in RANK_VALUES),
        required=False,
    )

    class Meta:
        model = Team
        fields = ('name', 'description', 'recruiting', 'preferred_role', 'minimum_rank')
        widgets = {'description': forms.Textarea(attrs={'rows': 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-control'


class TeamPlayerChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, player):
        owner = f'(@{player.owner.username})' if player.owner_id else '(unlinked record)'
        return f'{player.ign} {owner} · {player.main_role} · {player.current_rank}'


class TeamPlayerAddForm(forms.Form):
    player = TeamPlayerChoiceField(
        queryset=Player.objects.none(),
        empty_label='Choose a player profile',
        label='Available player',
    )

    def __init__(self, *args, team, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['player'].queryset = Player.objects.filter(
            available_for_team=True,
        ).filter(
            Q(owner__isnull=True) | Q(owner__community_profile__is_player=True),
        ).exclude(
            owner__team_memberships__team=team,
            owner__team_memberships__status__in=(
                TeamMembership.Status.REQUESTED,
                TeamMembership.Status.ACTIVE,
            ),
        ).exclude(
            team_roster_entries__team=team,
        ).select_related('owner').distinct().order_by('ign')
        self.fields['player'].widget.attrs['class'] = 'form-control'


class TournamentForm(forms.ModelForm):
    starts_at = forms.DateTimeField(
        input_formats=('%Y-%m-%dT%H:%M',),
        widget=forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'type': 'datetime-local'}),
    )
    registration_deadline = forms.DateTimeField(
        input_formats=('%Y-%m-%dT%H:%M',),
        widget=forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'type': 'datetime-local'}),
    )

    class Meta:
        model = Tournament
        fields = ('name', 'description', 'starts_at', 'registration_deadline', 'format', 'status')
        widgets = {'description': forms.Textarea(attrs={'rows': 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('starts_at')
        deadline = cleaned.get('registration_deadline')
        if start and deadline and deadline > start:
            self.add_error('registration_deadline', 'Registration must close before the tournament starts.')
        return cleaned


class AccountSettingsForm(forms.Form):
    email = forms.EmailField()
    is_player = forms.BooleanField(required=False, label='Player looking for a team')
    is_team_staff = forms.BooleanField(required=False, label='Captain, manager, or coach')
    is_tournament_organizer = forms.BooleanField(required=False, label='Tournament organizer')

    def __init__(self, *args, user, profile, **kwargs):
        self.user = user
        self.profile = profile
        super().__init__(*args, **kwargs)
        self.initial.setdefault('email', user.email)
        self.initial.setdefault('is_player', profile.is_player)
        self.initial.setdefault('is_team_staff', profile.is_team_staff)
        self.initial.setdefault('is_tournament_organizer', profile.is_tournament_organizer)
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'autocomplete': 'email'})

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        users = get_user_model().objects.filter(email__iexact=email).exclude(pk=self.user.pk)
        if users.exists():
            raise forms.ValidationError('An account with this email address already exists.')
        return email

    def clean(self):
        cleaned = super().clean()
        roles = ('is_player', 'is_team_staff', 'is_tournament_organizer')
        if not any(cleaned.get(role) for role in roles):
            raise forms.ValidationError('Keep at least one account responsibility selected.')
        if not cleaned.get('is_player') and Player.objects.filter(owner=self.user).exists():
            self.add_error('is_player', 'Delete your player profile before removing the player role.')
        manages_team = Team.objects.filter(
            Q(owner=self.user) | Q(
                memberships__user=self.user,
                memberships__status=TeamMembership.Status.ACTIVE,
                memberships__role__in=(TeamMembership.Role.CAPTAIN, TeamMembership.Role.MANAGER),
            )
        ).exists()
        if not cleaned.get('is_team_staff') and manages_team:
            self.add_error('is_team_staff', 'Transfer or disband your teams before removing the team staff role.')
        if not cleaned.get('is_tournament_organizer') and Tournament.objects.filter(organizer=self.user).exists():
            self.add_error('is_tournament_organizer', 'You still own tournaments; keep this role to manage them.')
        return cleaned

    @transaction.atomic
    def save(self):
        self.user.email = self.cleaned_data['email']
        self.user.save(update_fields=('email',))
        self.profile.is_player = self.cleaned_data['is_player']
        self.profile.is_team_staff = self.cleaned_data['is_team_staff']
        self.profile.is_tournament_organizer = self.cleaned_data['is_tournament_organizer']
        self.profile.save(update_fields=('is_player', 'is_team_staff', 'is_tournament_organizer'))
        return self.profile
