from django import forms

from .models import Player


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
