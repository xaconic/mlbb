from django.test import TestCase
from django.urls import reverse

from .forms import PlayerForm, RANK_GROUPS
from .models import Player


class DashboardViewTests(TestCase):
    def test_dashboard_displays_players(self):
        Player.objects.create(
            player_id=1,
            server=100,
            ign='TestIGN',
            main_role='Marksman',
            highest_rank='Gold',
            current_rank='Platinum',
            win_rate=58.50,
        )

        response = self.client.get(reverse('index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Player Dashboard')
        self.assertContains(response, 'TestIGN')

    def test_existing_player_gets_default_star_counts(self):
        player = Player.objects.create(
            player_id=2,
            server=100,
            ign='LegacyIGN',
            main_role='Roam',
            highest_rank='Legend',
            current_rank='Epic',
            win_rate=50,
        )

        self.assertEqual(player.highest_stars, 0)
        self.assertEqual(player.current_stars, 0)

    def test_add_player_saves_and_updates_dashboard(self):
        response = self.client.post(reverse('index'), {
            'player_id': '1404943950',
            'server': '11625',
            'ign': 'NewPlayer',
            'main_role': 'Roam',
            'highest_rank': 'Mythical Immortal',
            'highest_stars': '538',
            'current_rank': 'Mythical Glory',
            'current_stars': '77',
            'win_rate': '77.77',
        })

        self.assertRedirects(response, reverse('index'))
        player = Player.objects.get(player_id=1404943950)
        self.assertEqual(player.highest_stars, 538)
        self.assertEqual(player.current_stars, 77)
        dashboard = self.client.get(reverse('index'))
        self.assertContains(dashboard, 'NewPlayer')
        self.assertContains(dashboard, '538')
        self.assertContains(dashboard, '77.77%')

    def test_duplicate_player_id_shows_validation_error(self):
        Player.objects.create(
            player_id=3,
            server=100,
            ign='Existing',
            main_role='Roam',
            highest_rank='Legend',
            current_rank='Epic',
            win_rate=50,
        )

        response = self.client.post(reverse('index'), {
            'player_id': '3',
            'server': '100',
            'ign': 'Duplicate',
            'main_role': 'Roam',
            'highest_rank': 'Legend',
            'highest_stars': '0',
            'current_rank': 'Epic',
            'current_stars': '0',
            'win_rate': '50',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Player ID already exists.')
        self.assertEqual(Player.objects.count(), 1)

    def test_invalid_stars_and_win_rate_are_rejected(self):
        payload = {
            'player_id': '4',
            'server': '100',
            'ign': 'InvalidPlayer',
            'main_role': 'Roam',
            'highest_rank': 'Legend',
            'highest_stars': '-1',
            'current_rank': 'Epic',
            'current_stars': '1.5',
            'win_rate': '100.01',
        }

        response = self.client.post(reverse('index'), payload)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ensure this value is greater than or equal to 0.')
        self.assertContains(response, 'Enter a whole number.')
        self.assertContains(response, 'Ensure this value is less than or equal to 100.')
        self.assertFalse(Player.objects.filter(player_id=4).exists())

    def test_empty_post_keeps_form_open_with_required_errors(self):
        response = self.client.post(reverse('index'), {})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add New Player')
        self.assertContains(response, 'This field is required.')
        self.assertContains(response, 'id="player-modal"')
        self.assertFalse(Player.objects.exists())

    def test_high_star_counts_are_accepted(self):
        response = self.client.post(reverse('index'), {
            'player_id': '5',
            'server': '100',
            'ign': 'HighStarPlayer',
            'main_role': 'Gold Lane',
            'highest_rank': 'Mythical Immortal',
            'highest_stars': '5000',
            'current_rank': 'Mythical Immortal',
            'current_stars': '1000',
            'win_rate': '100',
        })

        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Player.objects.get(player_id=5).highest_stars, 5000)


class RankAndStarValidationTests(TestCase):
    def form_data(self, rank, stars, player_id=10000):
        return {
            'player_id': str(player_id),
            'server': '11625',
            'ign': 'RankTest',
            'main_role': 'Exp Lane',
            'highest_rank': rank,
            'highest_stars': str(stars),
            'current_rank': rank,
            'current_stars': str(stars),
            'win_rate': '77.77',
        }

    def test_rank_choices_are_exact_and_grouped(self):
        self.assertEqual(
            tuple(label for label, _ in RANK_GROUPS),
            ('Warrior', 'Elite', 'Master', 'Grandmaster', 'Epic', 'Legend', 'Mythic'),
        )
        options = tuple(value for _, group in RANK_GROUPS for value, _ in group)
        self.assertIn('Warrior III', options)
        self.assertIn('Legend I', options)
        self.assertIn('Mythic', options)
        self.assertNotIn('Warrior', options)
        self.assertNotIn('Legend', options)

    def test_valid_rank_star_combinations(self):
        valid_combinations = (
            ('Warrior III', 0),
            ('Elite II', 4),
            ('Master I', 4),
            ('Grandmaster IV', 5),
            ('Epic II', 10),
            ('Legend I', 18),
            ('Mythic', 15),
            ('Mythical Honor', 35),
            ('Mythical Glory', 77),
            ('Mythical Immortal', 538),
            ('Mythical Immortal', 1000),
            ('Mythical Immortal', 5000),
        )

        for player_id, (rank, stars) in enumerate(valid_combinations, start=10000):
            with self.subTest(rank=rank, stars=stars):
                form = PlayerForm(data=self.form_data(rank, stars, player_id))
                self.assertTrue(form.is_valid(), form.errors)
                self.assertEqual(form.cleaned_data['highest_rank'], rank)
                self.assertEqual(form.cleaned_data['current_rank'], rank)

    def test_invalid_mythic_rank_star_combinations_fail_for_both_ranks(self):
        invalid_combinations = (
            ('Mythic', 0), ('Mythic', 25), ('Mythic', 30),
            ('Mythical Honor', 24), ('Mythical Honor', 50), ('Mythical Honor', 60),
            ('Mythical Glory', 30), ('Mythical Glory', 49), ('Mythical Glory', 100),
            ('Mythical Immortal', 0), ('Mythical Immortal', 50), ('Mythical Immortal', 99),
        )

        for player_id, (rank, stars) in enumerate(invalid_combinations, start=20000):
            with self.subTest(rank=rank, stars=stars):
                form = PlayerForm(data=self.form_data(rank, stars, player_id))
                self.assertFalse(form.is_valid())
                self.assertIn('highest_stars', form.errors)
                self.assertIn('current_stars', form.errors)

    def test_non_integer_and_negative_stars_fail(self):
        for player_id, stars in enumerate(('-1', '1.5', '10.5', 'abc', ''), start=30000):
            with self.subTest(stars=stars):
                form = PlayerForm(data=self.form_data('Mythical Immortal', stars, player_id))
                self.assertFalse(form.is_valid())
                self.assertIn('highest_stars', form.errors)
                self.assertIn('current_stars', form.errors)

    def test_exp_lane_is_the_only_exp_role_value(self):
        role_values = tuple(value for value, _ in PlayerForm.base_fields['main_role'].choices)
        self.assertIn('Exp Lane', role_values)
        self.assertNotIn('EXP Lane', role_values)
        self.assertNotIn('EXP', role_values)
