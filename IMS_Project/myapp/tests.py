from datetime import timedelta
from io import BytesIO
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import urlsplit

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .forms import PlayerForm, RANK_GROUPS, TeamForm
from .mlbb_api import LookupError, lookup_player
from .models import (
    Hero,
    Player,
    PlayerHero,
    Team,
    TeamMembership,
    TeamRosterEntry,
    Tournament,
    TournamentEntry,
    UserProfile,
)


class DashboardViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='roster-manager',
            password='Safe-test-password-9284!',
        )
        UserProfile.objects.create(user=self.user, is_player=True, is_team_staff=True)
        self.heroes = list(Hero.objects.filter(is_active=True)[:6])
        self.client.force_login(self.user)

    def profile_data(self, **overrides):
        data = {
            'player_id': '1404943950',
            'server': '11625',
            'ign': 'NewPlayer',
            'main_role': 'Roam',
            'highest_rank': 'Mythical Immortal',
            'highest_stars': '538',
            'current_rank': 'Mythical Glory',
            'current_stars': '77',
            'win_rate': '77.77',
            'preferred_play_style': 'Shot caller',
            'biography': 'Looking for a competitive squad.',
            'available_for_team': 'on',
            'main_heroes': [str(hero.pk) for hero in self.heroes[:5]],
        }
        data.update(overrides)
        return data

    def test_dashboard_displays_players(self):
        Player.objects.create(
            owner=self.user,
            player_id=1,
            server=100,
            ign='TestIGN',
            main_role='Gold Lane',
            highest_rank='Epic V',
            current_rank='Epic V',
            win_rate=58.50,
        )

        response = self.client.get(reverse('index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Find your next')
        self.assertContains(response, 'TestIGN')

    def test_dashboard_lists_recent_player_records_first(self):
        recent = Player.objects.create(
            owner=self.user,
            player_id=10,
            server=100,
            ign='RecentPlayer',
            main_role='Gold Lane',
            highest_rank='Epic V',
            current_rank='Epic V',
            win_rate=58.50,
        )
        older_user = get_user_model().objects.create_user(username='older-player')
        UserProfile.objects.create(user=older_user, is_player=True)
        older = Player.objects.create(
            owner=older_user,
            player_id=11,
            server=100,
            ign='OlderPlayer',
            main_role='Roam',
            highest_rank='Legend I',
            current_rank='Legend I',
            win_rate=64,
        )
        Player.objects.filter(pk=older.pk).update(updated_at=timezone.now() - timedelta(days=2))

        response = self.client.get(reverse('index'))

        self.assertEqual(list(response.context['players']), [recent, older])
        self.assertContains(response, 'Recent player records')
        self.assertContains(response, 'Updated')

    def test_legacy_unowned_player_records_are_visible_only_to_team_staff(self):
        Player.objects.create(
            player_id=2, server=100, ign='LegacyIGN', main_role='Roam',
            highest_rank='Legend I', current_rank='Epic I', win_rate=50,
        )
        response = self.client.get(reverse('index'))
        self.assertContains(response, 'LegacyIGN')
        self.assertContains(response, 'UNLINKED PLAYER RECORDS')

        visitor = get_user_model().objects.create_user(username='community-player')
        UserProfile.objects.create(user=visitor, is_player=True)
        self.client.force_login(visitor)
        response = self.client.get(reverse('index'))
        self.assertNotContains(response, 'LegacyIGN')

    def test_discovery_filters_only_recruiting_profiles(self):
        player_user = get_user_model().objects.create_user(username='roam-scout')
        Player.objects.create(
            owner=player_user, player_id=22, server=90, ign='RoamScout',
            main_role='Roam', highest_rank='Legend I', current_rank='Epic I',
            win_rate=64, available_for_team=True,
        )
        player = Player.objects.get(owner=player_user)
        selected = self.heroes[:5]
        PlayerHero.objects.bulk_create([
            PlayerHero(player=player, hero=item, position=position)
            for position, item in enumerate(selected, start=1)
        ])
        team = Team.objects.create(name='Roam Seekers', owner=self.user)
        TeamMembership.objects.create(
            team=team, user=player_user, status=TeamMembership.Status.ACTIVE,
        )

        response = self.client.get(reverse('player-discovery'), {
            'q': 'Scout', 'role': 'Roam', 'rank': 'Legend I',
            'hero': selected[0].name, 'team': str(team.pk),
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'RoamScout')
        self.assertContains(self.client.get(reverse('teams')), 'Roam Seekers')

        player.available_for_team = False
        player.save(update_fields=('available_for_team',))
        response = self.client.get(reverse('player-discovery'), {'q': 'RoamScout'})
        self.assertEqual(response.context['page'].object_list.count(), 0)

    def test_existing_player_gets_default_star_counts(self):
        player = Player.objects.create(
            player_id=2,
            server=100,
            ign='LegacyIGN',
            main_role='Roam',
            highest_rank='Legend I',
            current_rank='Epic I',
            win_rate=50,
        )

        self.assertEqual(player.highest_stars, 0)
        self.assertEqual(player.current_stars, 0)

    def test_profile_saves_five_heroes_and_is_persisted(self):
        response = self.client.post(reverse('player-profile'), self.profile_data())
        self.assertRedirects(response, reverse('player-profile'))
        player = Player.objects.get(owner=self.user)
        self.assertEqual(player.highest_stars, 538)
        self.assertEqual(player.current_stars, 77)
        self.assertEqual(player.main_heroes.count(), 5)
        refreshed = self.client.get(reverse('player-profile'))
        self.assertContains(refreshed, 'NewPlayer')
        self.assertContains(refreshed, 'aria-label="5 of 5 heroes selected"')
        self.assertContains(refreshed, 'class="editor-section heroes-section hero-picker"')
        self.assertContains(refreshed, 'id="hero-count-value">5</span>')
        positions = list(player.hero_selections.values_list('position', flat=True))
        self.assertEqual(positions, [1, 2, 3, 4, 5])
        self.client.logout()
        self.client.login(username=self.user.username, password='Safe-test-password-9284!')
        self.assertEqual(Player.objects.get(owner=self.user).main_heroes.count(), 5)

    def test_profile_renders_catalog_portraits_with_lazy_loading(self):
        self.assertEqual(
            Hero.objects.filter(
                is_active=True,
                portrait_url__startswith='https://static.wikia.nocookie.net/mobile-legends/images/',
            ).count(),
            133,
        )
        self.assertEqual(Hero.objects.filter(is_active=True).count(), 133)
        response = self.client.get(reverse('player-profile'))
        self.assertContains(response, 'src="https://static.wikia.nocookie.net/mobile-legends/images/')
        self.assertContains(response, 'loading="lazy" decoding="async" referrerpolicy="strict-origin-when-cross-origin"')
        self.assertContains(response, 'https://mobile-legends.fandom.com/wiki/List_of_heroes')

    def test_hero_portrait_urls_are_limited_to_approved_sources(self):
        hero = Hero(name='External portrait check', portrait_url='https://images.example/portrait.png')
        with self.assertRaisesMessage(ValidationError, 'approved Mobile Legends artwork source'):
            hero.full_clean()
        Hero(
            name='Fandom portrait check',
            portrait_url='https://static.wikia.nocookie.net/mobile-legends/images/1/13/Hero551-icon.png',
        ).full_clean()

    def test_profile_requires_exactly_five_distinct_heroes(self):
        for selection in (self.heroes[:4], self.heroes):
            with self.subTest(selection_count=len(selection)):
                response = self.client.post(reverse('player-profile'), self.profile_data(
                    main_heroes=[str(hero.pk) for hero in selection],
                ))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'Choose exactly five distinct main heroes.')
        self.assertFalse(Player.objects.filter(owner=self.user).exists())

    def test_profile_rejects_duplicate_hero_ids_and_duplicate_game_id(self):
        duplicate_heroes = [str(hero.pk) for hero in self.heroes[:4]] + [str(self.heroes[0].pk)]
        response = self.client.post(reverse('player-profile'), self.profile_data(main_heroes=duplicate_heroes))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Player.objects.filter(owner=self.user).exists())

        player_user = get_user_model().objects.create_user(username='other-account')
        Player.objects.create(
            owner=player_user,
            player_id=1404943950,
            server=11625,
            ign='Existing',
            main_role='Roam',
            highest_rank='Legend I',
            current_rank='Epic I',
            win_rate=50,
        )
        response = self.client.post(reverse('player-profile'), self.profile_data())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'already associated with an account')

    def test_unlinked_player_record_can_be_claimed_by_account(self):
        legacy = Player.objects.create(
            player_id=1404943950,
            server=11625,
            ign='LegacyClaim',
            main_role='Roam',
            highest_rank='Legend I',
            current_rank='Epic I',
            win_rate=50,
        )

        response = self.client.post(reverse('player-profile'), self.profile_data(
            player_id='1404943950',
            server='11625',
            ign='LegacyClaim',
            main_role='Roam',
            highest_rank='Legend I',
            highest_stars='20',
            current_rank='Epic I',
            current_stars='5',
            win_rate='50',
        ))

        self.assertRedirects(response, reverse('player-profile'))
        legacy.refresh_from_db()
        self.assertEqual(legacy.owner, self.user)
        self.assertEqual(Player.objects.get(owner=self.user).ign, 'LegacyClaim')

    def test_player_id_can_repeat_only_on_a_different_server(self):
        first_user = get_user_model().objects.create_user(username='server-one')
        second_user = get_user_model().objects.create_user(username='server-two')
        Player.objects.create(
            owner=first_user, player_id=999, server=100, ign='OneServer',
            main_role='Roam', highest_rank='Legend I', current_rank='Epic I', win_rate=50,
        )
        other_server = Player.objects.create(
            owner=second_user, player_id=999, server=101, ign='OtherServer',
            main_role='Roam', highest_rank='Legend I', current_rank='Epic I', win_rate=50,
        )
        self.assertEqual(other_server.server, 101)

    def test_invalid_stars_and_win_rate_are_rejected(self):
        response = self.client.post(reverse('player-profile'), self.profile_data(
            highest_stars='-1', current_stars='1.5', win_rate='100.01',
        ))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ensure this value is greater than or equal to 0.')
        self.assertContains(response, 'Enter a whole number.')
        self.assertContains(response, 'Ensure this value is less than or equal to 100.')
        self.assertFalse(Player.objects.filter(owner=self.user).exists())

    def test_empty_profile_post_shows_required_errors(self):
        response = self.client.post(reverse('player-profile'), {})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Make your mark')
        self.assertContains(response, 'This field is required.')
        self.assertFalse(Player.objects.exists())

    def test_profile_can_be_edited_then_deleted(self):
        self.client.post(reverse('player-profile'), self.profile_data())
        response = self.client.post(reverse('player-profile'), self.profile_data(ign='UpdatedIGN'))
        self.assertRedirects(response, reverse('player-profile'))
        self.assertEqual(Player.objects.get(owner=self.user).ign, 'UpdatedIGN')
        response = self.client.post(reverse('player-profile'), {'action': 'delete'})
        self.assertRedirects(response, reverse('index'))
        self.assertFalse(Player.objects.filter(owner=self.user).exists())


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


class AuthenticationFlowTests(TestCase):
    def test_signup_creates_account_and_starts_authenticated_session(self):
        response = self.client.post(reverse('signup'), {
            'username': 'new-captain',
            'email': 'new-captain@example.com',
            'password1': 'Strong-unique-password-9284!',
            'password2': 'Strong-unique-password-9284!',
            'roles': ['player', 'staff'],
        })

        self.assertRedirects(response, reverse('player-profile'))
        self.assertTrue(get_user_model().objects.filter(username='new-captain').exists())
        self.assertIn('_auth_user_id', self.client.session)
        user = get_user_model().objects.get(username='new-captain')
        self.assertTrue(user.community_profile.is_player)
        self.assertTrue(user.community_profile.is_team_staff)

    def test_login_accepts_valid_credentials_and_logout_uses_post(self):
        user = get_user_model().objects.create_user(
            username='captain',
            password='Strong-unique-password-9284!',
        )

        response = self.client.post(reverse('login'), {
            'username': user.username,
            'password': 'Strong-unique-password-9284!',
        })

        self.assertRedirects(response, reverse('index'))
        self.assertIn('_auth_user_id', self.client.session)
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('login'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_login_accepts_account_email(self):
        user = get_user_model().objects.create_user(
            username='email-login',
            email='email-login@example.com',
            password='Strong-unique-password-9284!',
        )

        response = self.client.post(reverse('login'), {
            'username': user.email,
            'password': 'Strong-unique-password-9284!',
        })

        self.assertRedirects(response, reverse('index'))
        self.assertIn('_auth_user_id', self.client.session)

    def test_invalid_login_stays_on_login_form(self):
        response = self.client.post(reverse('login'), {
            'username': 'unknown',
            'password': 'incorrect',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter a correct username and password')

    def test_roster_writes_and_lookup_require_login(self):
        root_response = self.client.get(reverse('index'))
        self.assertEqual(root_response.status_code, 302)
        self.assertEqual(root_response.url, f"{reverse('login')}?next=/")
        response = self.client.post(reverse('player_lookup'), data='{}', content_type='application/json')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"{reverse('login')}?next=/api/player-lookup/")

    def test_auth_pages_render(self):
        self.assertContains(self.client.get(reverse('login')), 'Sign in to your account')
        signup = self.client.get(reverse('signup'))
        self.assertContains(signup, 'Create your account')
        self.assertContains(signup, 'class="auth-role-field"')
        self.assertContains(signup, 'Select every way you plan to use the hub.')

    def test_authenticated_password_change_keeps_session(self):
        user = get_user_model().objects.create_user(
            username='password-change-user',
            password='Strong-unique-password-9284!',
            email='password-change@example.com',
        )
        self.client.force_login(user)
        response = self.client.post(reverse('password-change'), {
            'old_password': 'Strong-unique-password-9284!',
            'new_password1': 'New-strong-password-3275!',
            'new_password2': 'New-strong-password-3275!',
        })
        self.assertRedirects(response, reverse('account-settings'))
        user.refresh_from_db()
        self.assertTrue(user.check_password('New-strong-password-3275!'))
        self.assertIn('_auth_user_id', self.client.session)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_password_reset_email_and_confirmation_flow(self):
        user = get_user_model().objects.create_user(
            username='recovery-user',
            email='recovery@example.com',
            password='Strong-unique-password-9284!',
        )
        response = self.client.post(reverse('password-reset'), {'email': user.email})
        self.assertRedirects(response, reverse('password-reset-done'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('/accounts/reset/', mail.outbox[0].body)

        reset_url = next(
            line for line in mail.outbox[0].body.splitlines()
            if '/accounts/reset/' in line
        )
        path = urlsplit(reset_url).path
        response = self.client.get(path)
        self.assertEqual(response.status_code, 302)
        response = self.client.get(response.url)
        self.assertContains(response, 'Choose a new password')
        response = self.client.post(response.request['PATH_INFO'], {
            'new_password1': 'New-strong-password-3275!',
            'new_password2': 'New-strong-password-3275!',
        })
        self.assertRedirects(response, reverse('password-reset-complete'))
        user.refresh_from_db()
        self.assertTrue(user.check_password('New-strong-password-3275!'))


class PlayerLookupProviderTests(TestCase):
    @patch('myapp.mlbb_api.urlopen')
    def test_lookup_normalizes_valid_response(self, urlopen):
        response = type('Response', (), {
            'status': 200,
            'read': lambda self: b'{"success":true,"id":"123","server":"45","name":"Luna","role":"Roam"}',
            '__enter__': lambda self: self,
            '__exit__': lambda self, *args: None,
        })()
        urlopen.return_value = response
        result = lookup_player('123', '45')
        self.assertEqual(result['ign'], 'Luna')
        self.assertEqual(result['main_role'], 'Roam')
        self.assertEqual(result['player_id'], 123)

    @patch('myapp.mlbb_api.urlopen', side_effect=TimeoutError())
    def test_lookup_timeout_is_reported(self, _urlopen):
        with self.assertRaises(LookupError) as raised:
            lookup_player('123', '45')
        self.assertEqual(raised.exception.status, 504)

    @patch('myapp.mlbb_api.urlopen')
    def test_lookup_http_error_is_reported_without_provider_body(self, urlopen):
        urlopen.side_effect = HTTPError(
            'https://example.invalid', 500, 'upstream error', {}, BytesIO(b'private detail'),
        )
        with self.assertRaises(LookupError) as raised:
            lookup_player('123', '45')
        self.assertEqual(raised.exception.status, 502)
        self.assertNotIn('private detail', raised.exception.message)

    @patch('myapp.mlbb_api.urlopen')
    def test_lookup_retries_a_fallback_endpoint_when_primary_provider_fails(self, urlopen):
        primary_error = HTTPError(
            'https://api.isan.eu.org/nickname/ml?id=123&server=45',
            500,
            'upstream error',
            {},
            BytesIO(b'private detail'),
        )
        response = type('Response', (), {
            'status': 200,
            'read': lambda self: b'{"success":true,"id":"123","server":"45","name":"Nova","role":"Jungle"}',
            '__enter__': lambda self: self,
            '__exit__': lambda self, *args: None,
        })()
        urlopen.side_effect = [primary_error, response]

        result = lookup_player('123', '45')

        self.assertEqual(result['ign'], 'Nova')
        self.assertEqual(urlopen.call_count, 2)

    @patch('myapp.mlbb_api.urlopen')
    def test_lookup_rejects_malformed_payload(self, urlopen):
        response = type('Response', (), {
            'status': 200,
            'read': lambda self: b'<html>not json</html>',
            '__enter__': lambda self: self,
            '__exit__': lambda self, *args: None,
        })()
        urlopen.return_value = response
        with self.assertRaises(LookupError) as raised:
            lookup_player('123', '45')
        self.assertEqual(raised.exception.status, 502)


class PlayerLookupViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='lookup-user')
        self.client.force_login(self.user)

    @patch('myapp.views.lookup_player')
    def test_authenticated_lookup_returns_normalized_player(self, lookup):
        lookup.return_value = {
            'player_id': 123, 'server': 45, 'ign': 'Lookup IGN',
            'main_role': 'Roam', 'current_rank': 'Epic I',
            'highest_rank': 'Legend I', 'current_stars': 5,
            'highest_stars': 20, 'win_rate': 61.5,
        }
        response = self.client.post(
            reverse('player_lookup'),
            data='{"player_id":"123","server_id":"45"}',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['player']['ign'], 'Lookup IGN')

    @patch('myapp.views.lookup_player', side_effect=LookupError('Provider unavailable.', status=503))
    def test_provider_error_is_returned_to_profile_client(self, _lookup):
        response = self.client.post(
            reverse('player_lookup'),
            data='{"player_id":"123","server_id":"45"}',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()['error'], 'Provider unavailable.')

    def test_lookup_requires_post_json_and_valid_identifiers(self):
        self.assertEqual(self.client.get(reverse('player_lookup')).status_code, 405)
        response = self.client.post(
            reverse('player_lookup'), data='{"player_id":"0","server_id":"45"}',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)


class TeamWorkflowTests(TestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(username='team-owner')
        UserProfile.objects.create(user=self.owner, is_player=False, is_team_staff=True)
        self.member = get_user_model().objects.create_user(username='candidate')
        UserProfile.objects.create(user=self.member, is_player=True)
        self.team = Team.objects.create(name='Blue Lanterns', owner=self.owner)
        TeamMembership.objects.create(
            team=self.team, user=self.owner, role=TeamMembership.Role.CAPTAIN,
            status=TeamMembership.Status.ACTIVE,
        )

    def test_captain_approves_join_request_and_sets_member_role(self):
        self.client.force_login(self.member)
        request = self.client.post(reverse('team-detail', args=(self.team.pk,)), {
            'action': 'request_join',
        })
        self.assertEqual(request.status_code, 302)
        membership = TeamMembership.objects.get(team=self.team, user=self.member)
        self.assertEqual(membership.status, TeamMembership.Status.REQUESTED)

        self.client.force_login(self.owner)
        response = self.client.post(reverse('team-detail', args=(self.team.pk,)), {
            'action': 'review_membership',
            'membership_id': membership.pk,
            'decision': 'accept',
        })
        self.assertEqual(response.status_code, 302)
        membership.refresh_from_db()
        self.assertEqual(membership.status, TeamMembership.Status.ACTIVE)

        response = self.client.post(reverse('team-detail', args=(self.team.pk,)), {
            'action': 'update_role',
            'membership_id': membership.pk,
            'role': TeamMembership.Role.COACH,
        })
        self.assertEqual(response.status_code, 302)
        membership.refresh_from_db()
        self.assertEqual(membership.role, TeamMembership.Role.COACH)

    def test_non_member_cannot_remove_or_promote_members(self):
        membership = TeamMembership.objects.create(
            team=self.team, user=self.member, status=TeamMembership.Status.ACTIVE,
        )
        outsider = get_user_model().objects.create_user(username='outsider')
        self.client.force_login(outsider)
        self.client.post(reverse('team-detail', args=(self.team.pk,)), {
            'action': 'remove_member', 'membership_id': membership.pk,
        })
        membership.refresh_from_db()
        self.assertEqual(membership.status, TeamMembership.Status.ACTIVE)

    def test_declined_player_can_reapply_to_recruiting_team(self):
        membership = TeamMembership.objects.create(
            team=self.team, user=self.member, status=TeamMembership.Status.DECLINED,
        )
        self.client.force_login(self.member)
        response = self.client.get(reverse('team-detail', args=(self.team.pk,)))
        self.assertContains(response, 'Request again')
        self.client.post(reverse('team-detail', args=(self.team.pk,)), {'action': 'request_join'})
        membership.refresh_from_db()
        self.assertEqual(membership.status, TeamMembership.Status.REQUESTED)

    def test_only_team_staff_role_can_create_a_team(self):
        self.client.force_login(self.member)
        response = self.client.post(reverse('teams'), {
            'name': 'Unauthorized Team',
        })
        self.assertRedirects(response, reverse('teams'))
        self.assertFalse(Team.objects.filter(name='Unauthorized Team').exists())

    def test_team_pages_render_and_owner_can_edit(self):
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(reverse('teams')).status_code, 200)
        response = self.client.get(reverse('team-detail', args=(self.team.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add a player')
        self.assertContains(response, 'No available player records yet.')
        self.assertEqual(self.client.get(reverse('team-edit', args=(self.team.pk,))).status_code, 200)

    def test_team_manager_can_add_an_available_player_profile(self):
        player = Player.objects.create(
            owner=self.member,
            player_id=1200,
            server=100,
            ign='AvailableScout',
            main_role='Jungle',
            highest_rank='Epic V',
            current_rank='Epic V',
            win_rate=63,
        )
        self.client.force_login(self.owner)

        response = self.client.get(reverse('team-detail', args=(self.team.pk,)))
        self.assertContains(response, 'AvailableScout (@candidate)')
        response = self.client.post(reverse('team-detail', args=(self.team.pk,)), {
            'action': 'add_player',
            'player': str(player.pk),
        })

        self.assertRedirects(response, reverse('team-detail', args=(self.team.pk,)))
        membership = TeamMembership.objects.get(team=self.team, user=self.member)
        self.assertEqual(membership.status, TeamMembership.Status.ACTIVE)
        self.assertEqual(membership.role, TeamMembership.Role.PLAYER)
        self.assertContains(self.client.get(reverse('team-detail', args=(self.team.pk,))), 'AvailableScout')

    def test_team_manager_can_add_and_remove_an_unlinked_player_record(self):
        player = Player.objects.create(
            player_id=1202,
            server=100,
            ign='LegacyScout',
            main_role='Mid Lane',
            highest_rank='Legend I',
            current_rank='Epic I',
            win_rate=61,
        )
        self.client.force_login(self.owner)

        response = self.client.get(reverse('team-detail', args=(self.team.pk,)))
        self.assertContains(response, 'LegacyScout (unlinked record)')
        response = self.client.post(reverse('team-detail', args=(self.team.pk,)), {
            'action': 'add_player',
            'player': str(player.pk),
        })
        self.assertRedirects(response, reverse('team-detail', args=(self.team.pk,)))
        entry = TeamRosterEntry.objects.get(team=self.team, player=player)
        self.assertEqual(entry.added_by, self.owner)
        self.assertContains(self.client.get(reverse('team-detail', args=(self.team.pk,))), 'LegacyScout')

        response = self.client.post(reverse('team-detail', args=(self.team.pk,)), {
            'action': 'remove_roster_entry',
            'roster_entry_id': str(entry.pk),
        })
        self.assertRedirects(response, reverse('team-detail', args=(self.team.pk,)))
        self.assertFalse(TeamRosterEntry.objects.filter(pk=entry.pk).exists())

    def test_only_team_managers_can_add_player_profiles(self):
        player = Player.objects.create(
            owner=self.member,
            player_id=1201,
            server=100,
            ign='AvailableScout',
            main_role='Jungle',
            highest_rank='Epic V',
            current_rank='Epic V',
            win_rate=63,
        )
        outsider = get_user_model().objects.create_user(username='roster-outsider')
        self.client.force_login(outsider)

        response = self.client.post(reverse('team-detail', args=(self.team.pk,)), {
            'action': 'add_player',
            'player': str(player.pk),
        })

        self.assertRedirects(response, reverse('team-detail', args=(self.team.pk,)))
        self.assertFalse(TeamMembership.objects.filter(team=self.team, user=self.member).exists())

    def test_team_recruitment_filters_reject_unknown_values(self):
        form = TeamForm(data={
            'name': 'Invalid Filters',
            'preferred_role': 'Unlisted role',
            'minimum_rank': 'Unlisted rank',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('preferred_role', form.errors)
        self.assertIn('minimum_rank', form.errors)


class TournamentWorkflowTests(TestCase):
    def setUp(self):
        self.organizer = get_user_model().objects.create_user(username='event-organizer')
        UserProfile.objects.create(user=self.organizer, is_player=False, is_tournament_organizer=True)
        self.owner = get_user_model().objects.create_user(username='team-captain')
        UserProfile.objects.create(user=self.owner, is_player=False, is_team_staff=True)
        self.team = Team.objects.create(name='Tournament Team', owner=self.owner)
        TeamMembership.objects.create(
            team=self.team, user=self.owner, role=TeamMembership.Role.CAPTAIN,
            status=TeamMembership.Status.ACTIVE,
        )
        self.tournament = Tournament.objects.create(
            name='Open Cup',
            organizer=self.organizer,
            starts_at=timezone.now() + timedelta(days=10),
            registration_deadline=timezone.now() + timedelta(days=5),
        )

    def test_team_manager_registers_and_organizer_reviews_entry(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse('tournament-detail', args=(self.tournament.pk,)), {
            'action': 'register', 'team_id': self.team.pk,
        })
        self.assertEqual(response.status_code, 302)
        entry = TournamentEntry.objects.get(tournament=self.tournament, team=self.team)
        self.assertEqual(entry.status, TournamentEntry.Status.REQUESTED)

        self.client.force_login(self.organizer)
        response = self.client.post(reverse('tournament-detail', args=(self.tournament.pk,)), {
            'action': 'review_entry', 'entry_id': entry.pk, 'decision': 'accept',
        })
        self.assertEqual(response.status_code, 302)
        entry.refresh_from_db()
        self.assertEqual(entry.status, TournamentEntry.Status.ACCEPTED)

    def test_team_can_resubmit_a_declined_tournament_entry(self):
        entry = TournamentEntry.objects.create(
            tournament=self.tournament, team=self.team, status=TournamentEntry.Status.DECLINED,
        )
        self.client.force_login(self.owner)
        response = self.client.get(reverse('tournament-detail', args=(self.tournament.pk,)))
        self.assertContains(response, 'Register')
        self.client.post(reverse('tournament-detail', args=(self.tournament.pk,)), {
            'action': 'register', 'team_id': self.team.pk,
        })
        entry.refresh_from_db()
        self.assertEqual(entry.status, TournamentEntry.Status.REQUESTED)

    def test_unrelated_user_cannot_register_another_teams_entry(self):
        outsider = get_user_model().objects.create_user(username='random-user')
        self.client.force_login(outsider)
        response = self.client.post(reverse('tournament-detail', args=(self.tournament.pk,)), {
            'action': 'register', 'team_id': self.team.pk,
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(TournamentEntry.objects.filter(team=self.team).exists())

    def test_tournament_pages_render_and_only_organizer_can_delete(self):
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(reverse('tournaments')).status_code, 200)
        self.assertEqual(self.client.get(reverse('tournament-detail', args=(self.tournament.pk,))).status_code, 200)
        self.client.post(reverse('tournament-edit', args=(self.tournament.pk,)), {'action': 'delete'})
        self.assertTrue(Tournament.objects.filter(pk=self.tournament.pk).exists())
        self.client.force_login(self.organizer)
        self.assertEqual(self.client.get(reverse('tournament-edit', args=(self.tournament.pk,))).status_code, 200)


class AccountAndNotificationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='account-user', email='account@example.com',
        )
        UserProfile.objects.create(user=self.user, is_player=True)
        self.client.force_login(self.user)

    def test_account_settings_update_email_and_multiple_roles(self):
        response = self.client.post(reverse('account-settings'), {
            'email': 'updated@example.com',
            'is_player': 'on',
            'is_team_staff': 'on',
            'is_tournament_organizer': 'on',
        })
        self.assertRedirects(response, reverse('account-settings'))
        self.user.refresh_from_db()
        self.user.community_profile.refresh_from_db()
        self.assertEqual(self.user.email, 'updated@example.com')
        self.assertTrue(self.user.community_profile.is_team_staff)
        self.assertTrue(self.user.community_profile.is_tournament_organizer)

    def test_account_cannot_remove_player_role_while_profile_exists(self):
        Player.objects.create(
            owner=self.user, player_id=654, server=98, ign='ProtectedProfile',
            main_role='Roam', highest_rank='Legend I', current_rank='Epic I', win_rate=51,
        )
        response = self.client.post(reverse('account-settings'), {
            'email': self.user.email,
            'is_team_staff': 'on',
        })
        self.assertEqual(response.status_code, 200)
        self.user.community_profile.refresh_from_db()
        self.assertTrue(self.user.community_profile.is_player)
        self.assertContains(response, 'Delete your player profile before removing the player role.')

    def test_notifications_show_only_relevant_activities(self):
        staff = get_user_model().objects.create_user(username='notification-staff')
        UserProfile.objects.create(user=staff, is_team_staff=True, is_player=False)
        team = Team.objects.create(name='Notification Team', owner=staff)
        TeamMembership.objects.create(
            team=team, user=staff, role=TeamMembership.Role.CAPTAIN,
            status=TeamMembership.Status.ACTIVE,
        )
        TeamMembership.objects.create(team=team, user=self.user)
        response = self.client.get(reverse('notifications'))
        self.assertContains(response, 'Notification Team')
        self.client.force_login(staff)
        response = self.client.get(reverse('notifications'))
        self.assertContains(response, 'account-user wants to join Notification Team')
        self.assertEqual(response.status_code, 200)


class AnalyticsPageTests(TestCase):
    def setUp(self):
        self.viewer = get_user_model().objects.create_user(
            username='analytics-viewer',
            password='Safe-test-password-9284!',
        )
        UserProfile.objects.create(user=self.viewer, is_player=True)
        self.client.force_login(self.viewer)

    def create_player(self, username, player_id, rank, stars, win_rate, **overrides):
        user = get_user_model().objects.create_user(username=username)
        UserProfile.objects.create(user=user, is_player=True)
        data = {
            'owner': user,
            'player_id': player_id,
            'server': 100,
            'ign': username,
            'main_role': 'Jungle',
            'highest_rank': rank,
            'current_rank': rank,
            'current_stars': stars,
            'highest_stars': stars,
            'win_rate': win_rate,
            'available_for_team': True,
        }
        data.update(overrides)
        return Player.objects.create(**data)

    def test_leaderboard_orders_real_players_by_rank_then_stars(self):
        first = self.create_player('rank-first', 101, 'Mythical Honor', 25, 60)
        second = self.create_player('rank-second', 102, 'Mythic', 24, 99)
        opted_out = self.create_player(
            'private-player', 103, 'Mythical Immortal', 100, 100,
            available_for_team=False,
        )
        portrait = Hero.objects.create(
            name='Leaderboard portrait hero',
            role='Jungle',
            portrait_url='https://static.wikia.nocookie.net/mobile-legends/images/test.png',
        )
        PlayerHero.objects.create(player=first, hero=portrait, position=1)

        response = self.client.get(reverse('player-leaderboard'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [player.pk for player in response.context['page'].object_list],
            [first.pk, second.pk],
        )
        self.assertEqual(response.context['podium'], [first, second])
        self.assertContains(response, 'community records, not verified game-server rankings')
        self.assertContains(response, 'Leaderboard portrait hero portrait')
        self.assertNotContains(response, opted_out.ign)

    def test_leaderboard_filters_by_search_role_rank_server_and_team(self):
        matching = self.create_player(
            'find-me', 201, 'Mythical Honor', 25, 74.5, server=201,
        )
        unrelated = self.create_player(
            'other-player', 202, 'Mythical Honor', 35, 88, server=201,
            main_role='Roam',
        )
        team = Team.objects.create(name='Analytics Squad', owner=self.viewer)
        TeamRosterEntry.objects.create(
            team=team, player=matching, added_by=self.viewer,
        )

        response = self.client.get(reverse('player-leaderboard'), {
            'q': 'find', 'role': 'Jungle', 'rank': 'Mythical Honor',
            'server': '201', 'team': str(team.pk),
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [player.pk for player in response.context['page'].object_list],
            [matching.pk],
        )
        self.assertNotContains(response, unrelated.ign)

    def test_leaderboard_recalculates_after_player_update_and_delete(self):
        leader = self.create_player('leader-before', 301, 'Mythic', 24, 60)
        challenger = self.create_player('challenger', 302, 'Mythic', 15, 70)
        response = self.client.get(reverse('player-leaderboard'))
        self.assertEqual(response.context['podium'][0].pk, leader.pk)

        leader.current_stars = 10
        leader.save()
        response = self.client.get(reverse('player-leaderboard'))
        self.assertEqual(response.context['podium'][0].pk, challenger.pk)

        challenger.delete()
        response = self.client.get(reverse('player-leaderboard'))
        self.assertEqual(response.context['total_players'], 1)
        self.assertEqual(response.context['podium'][0].pk, leader.pk)

    def test_win_rate_sort_and_pagination(self):
        higher_rank = self.create_player('higher-rank', 401, 'Mythic', 20, 60)
        higher_rate = self.create_player('higher-rate', 402, 'Legend I', 5, 90)

        response = self.client.get(reverse('player-leaderboard'), {'sort': 'win_rate'})
        self.assertEqual(response.context['podium'][0].pk, higher_rate.pk)

        for index in range(25):
            self.create_player(
                f'pagination-player-{index:02d}', 410 + index, 'Warrior III', 0, 50,
            )
        response = self.client.get(reverse('player-leaderboard'), {'page': '2'})
        self.assertEqual(response.context['page'].number, 2)
        self.assertEqual(len(response.context['page'].object_list), 2)
        self.assertEqual(
            [player.leaderboard_position for player in response.context['page'].object_list],
            [26, 27],
        )
        self.assertIn(higher_rank.pk, [player.pk for player in response.context['podium']])

    def test_dashboard_analytics_use_real_records_and_exclude_invalid_win_rate(self):
        self.create_player('valid-analytics', 501, 'Mythic', 10, 80)
        self.create_player('invalid-analytics', 502, 'Epic I', 2, 140)

        response = self.client.get(reverse('index'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.context['avg_win_rate']), '80')
        self.assertEqual(response.context['total_players'], 2)
        self.assertEqual(response.context['rank_distribution'][0]['current_rank'], 'Mythic')
        self.assertContains(response, 'Statistics not connected')

    def test_hero_catalog_search_lane_and_detail(self):
        hero = Hero.objects.create(
            name='Catalog Test Hero', role='Mid Lane', is_active=True,
        )
        Hero.objects.create(name='Other Catalog Hero', role='Roam', is_active=True)

        response = self.client.get(reverse('hero-catalog'), {
            'q': 'Catalog Test', 'lane': 'Mid Lane',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['page'].object_list), [hero])
        self.assertContains(response, 'Meta data unavailable')

        detail = self.client.get(reverse('hero-detail', args=(hero.pk,)))
        self.assertEqual(detail.status_code, 200)
        self.assertContains(detail, 'Catalog Test Hero')
        self.assertContains(detail, 'not available from a verified, authorized source')

    def test_analytics_pages_require_login(self):
        self.client.logout()
        response = self.client.get(reverse('player-leaderboard'))
        self.assertRedirects(response, f'{reverse("login")}?next={reverse("player-leaderboard")}')
        response = self.client.get(reverse('hero-catalog'))
        self.assertEqual(response.status_code, 302)
