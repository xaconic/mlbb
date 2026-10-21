import json
import logging

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Avg, Case, Count, IntegerField, Q, Value, When
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import (
    AccountSettingsForm,
    PlayerProfileForm,
    RANK_GROUPS,
    RANK_VALUES,
    RegistrationForm,
    ROLES,
    StyledAuthenticationForm,
    TeamForm,
    TeamPlayerAddForm,
    TournamentForm,
)
from .models import (
    Hero,
    Player,
    Team,
    TeamMembership,
    TeamRosterEntry,
    Tournament,
    TournamentEntry,
    UserProfile,
)
from .mlbb_api import LookupError, _validate_identifier, lookup_player


logger = logging.getLogger(__name__)


def _rank_order_expression():
    return Case(
        *[
            When(current_rank=value, then=Value(index))
            for index, value in enumerate(RANK_VALUES)
        ],
        default=Value(-1),
        output_field=IntegerField(),
    )


class PlayerLoginView(LoginView):
    authentication_form = StyledAuthenticationForm
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return self.get_redirect_url() or super().get_success_url()


def signup(request):
    if request.user.is_authenticated:
        return redirect('index')

    form = RegistrationForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Your account is ready. Welcome!')
        next_url = request.POST.get('next', '')
        if next_url and url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return redirect(next_url)
        if 'player' in form.cleaned_data['roles']:
            return redirect('player-profile')
        return redirect('index')

    return render(request, 'registration/signup.html', {
        'form': form,
        'next': request.POST.get('next', request.GET.get('next', '')),
    })


@require_POST
def signout(request):
    logout(request)
    messages.success(request, 'You have been signed out.')
    return redirect('login')


def _json_body(request):
    try:
        data = json.loads(request.body)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


@login_required
def player_lookup(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST request required.'}, status=405)
    data = _json_body(request)
    if data is None:
        return JsonResponse({'success': False, 'error': 'Invalid request.'}, status=400)
    try:
        player_id = _validate_identifier(data.get('player_id'), 'Player ID')
        server_id = _validate_identifier(data.get('server_id', data.get('server')), 'Server ID')
        player = lookup_player(player_id, server_id)
    except LookupError as error:
        if error.status >= 500:
            logger.warning('MLBB player lookup failed: %s', error.message)
        return JsonResponse({'success': False, 'error': error.message}, status=error.status)
    except Exception:
        logger.exception('Unexpected error during MLBB player lookup')
        return JsonResponse(
            {
                'success': False,
                'error': 'The MLBB lookup service failed unexpectedly. Please try again.',
            },
            status=502,
        )
    existing = Player.objects.filter(
        player_id=player['player_id'], server=player['server']
    ).first()
    player['duplicate'] = existing is not None
    if existing:
        player['existing'] = {
            'main_role': existing.main_role,
            'highest_rank': existing.highest_rank,
            'highest_stars': existing.highest_stars,
            'current_rank': existing.current_rank,
            'current_stars': existing.current_stars,
            'win_rate': str(existing.win_rate),
        }
    return JsonResponse({'success': True, 'player': player})


@login_required
def index(request):
    players = Player.objects.filter(
        owner__isnull=False,
        available_for_team=True,
    ).select_related('owner').prefetch_related('main_heroes').order_by('-updated_at', 'ign')
    teams = Team.objects.filter(recruiting=True).select_related('owner').prefetch_related('memberships')
    tournaments = Tournament.objects.exclude(status=Tournament.Status.COMPLETED)
    avg_win_rate = players.filter(
        win_rate__gte=0,
        win_rate__lte=100,
    ).aggregate(avg_win_rate=Avg('win_rate'))['avg_win_rate'] or 0
    rank_distribution = list(
        players.values('current_rank').annotate(total=Count('pk')).order_by(
            _rank_order_expression().desc()
        )
    )
    role_distribution = list(
        players.values('main_role').annotate(total=Count('pk')).order_by('-total', 'main_role')
    )
    for distribution in (rank_distribution, role_distribution):
        max_count = max((item['total'] for item in distribution), default=0)
        for item in distribution:
            item['percentage'] = round(item['total'] / max_count * 100) if max_count else 0
    top_ranked_players = Player.objects.filter(
        owner__isnull=False,
        available_for_team=True,
    ).select_related('owner').order_by(
        _rank_order_expression().desc(),
        '-current_stars',
        '-win_rate',
        'ign',
    )[:5]
    legacy_players = Player.objects.none()
    if UserProfile.objects.filter(user=request.user, is_team_staff=True).exists():
        legacy_players = Player.objects.filter(
            owner__isnull=True,
            available_for_team=True,
        ).order_by('-updated_at', 'ign')[:6]
    return render(request, 'dashboard.html', {
        'players': players[:6],
        'legacy_players': legacy_players,
        'teams': teams[:6],
        'tournaments': tournaments[:4],
        'total_players': players.count(),
        'total_teams': teams.count(),
        'avg_win_rate': avg_win_rate,
        'rank_distribution': rank_distribution,
        'role_distribution': role_distribution,
        'top_ranked_players': top_ranked_players,
        'my_player': Player.objects.filter(owner=request.user).first(),
    })


@login_required
def player_profile(request):
    player = Player.objects.filter(owner=request.user).first()
    roles, _ = UserProfile.objects.get_or_create(user=request.user)
    if not roles.is_player:
        messages.error(request, 'Your account does not have the player role.')
        return redirect('index')
    form_instance = player
    if request.method == 'POST':
        posted_player_id = request.POST.get('player_id', '').strip()
        posted_server = request.POST.get('server', '').strip()
        if (posted_player_id and posted_server and posted_player_id.isdigit() and posted_server.isdigit() and not player):
            form_instance = Player.objects.filter(
                player_id=int(posted_player_id),
                server=int(posted_server),
                owner__isnull=True,
            ).first() or form_instance
    form = PlayerProfileForm(request.POST if request.method == 'POST' else None, instance=form_instance)
    if request.method == 'POST' and request.POST.get('action') == 'delete':
        if player:
            player.delete()
            messages.success(request, 'Your player profile was deleted.')
        return redirect('index')
    if request.method == 'POST' and form.is_valid():
        form.instance.owner = request.user
        try:
            form.save()
        except IntegrityError:
            logger.exception('Unable to save player profile for user %s', request.user.pk)
            form.add_error('player_id', 'That player ID is already associated with an account on this server.')
        else:
            messages.success(request, 'Your player profile and five main heroes are saved.')
            return redirect('player-profile')
    return render(request, 'community/player_profile.html', {
        'form': form,
        'player': player,
        'heroes': list(Hero.objects.filter(is_active=True).values('id', 'name', 'role', 'portrait_url')),
        'selected_hero_count': player.main_heroes.count() if player else 0,
    })


@login_required
def player_discovery(request):
    players = Player.objects.filter(
        owner__isnull=False,
    ).select_related('owner').prefetch_related('main_heroes', 'owner__team_memberships__team')
    query = request.GET.get('q', '').strip()
    role = request.GET.get('role', '').strip()
    rank = request.GET.get('rank', '').strip()
    hero = request.GET.get('hero', '').strip()
    team_id = request.GET.get('team', '').strip()
    if query:
        players = players.filter(Q(ign__icontains=query) | Q(owner__username__icontains=query))
    if role:
        players = players.filter(main_role=role)
    if rank:
        players = players.filter(Q(current_rank=rank) | Q(highest_rank=rank))
    if hero:
        players = players.filter(main_heroes__name=hero)
    if team_id.isdecimal():
        players = players.filter(owner__team_memberships__team_id=int(team_id),
                                 owner__team_memberships__status=TeamMembership.Status.ACTIVE)
    paginator = Paginator(players.filter(available_for_team=True).distinct(), 12)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'community/player_discovery.html', {
        'page': page, 'query': query, 'role': role, 'rank': rank, 'hero': hero, 'team_id': team_id,
        'heroes': Hero.objects.filter(is_active=True),
        'teams': Team.objects.filter(recruiting=True),
        'ranks': tuple(rank for _, group in RANK_GROUPS for rank, _ in group),
    })


@login_required
def player_leaderboard(request):
    players = (
        Player.objects.filter(owner__isnull=False, available_for_team=True)
        .select_related('owner')
        .prefetch_related(
            'hero_selections__hero',
            'team_roster_entries__team',
            'owner__team_memberships__team',
        )
    )
    query = request.GET.get('q', '').strip()
    role = request.GET.get('role', '').strip()
    rank = request.GET.get('rank', '').strip()
    server = request.GET.get('server', '').strip()
    team_id = request.GET.get('team', '').strip()
    sort = request.GET.get('sort', 'rank')
    if sort not in {'rank', 'win_rate'}:
        sort = 'rank'

    if query:
        players = players.filter(ign__icontains=query)
    if role in dict(ROLES):
        players = players.filter(main_role=role)
    else:
        role = ''
    if rank in RANK_VALUES:
        players = players.filter(current_rank=rank)
    else:
        rank = ''
    if server.isdecimal():
        players = players.filter(server=int(server))
    else:
        server = ''
    if team_id.isdecimal():
        players = players.filter(
            Q(team_roster_entries__team_id=int(team_id))
            | Q(
                owner__team_memberships__team_id=int(team_id),
                owner__team_memberships__status=TeamMembership.Status.ACTIVE,
            )
        ).distinct()
    else:
        team_id = ''

    rank_order = _rank_order_expression()
    if sort == 'win_rate':
        players = players.order_by('-win_rate', rank_order.desc(), '-current_stars', 'ign')
    else:
        players = players.order_by(rank_order.desc(), '-current_stars', '-win_rate', 'ign')

    page = Paginator(players, 25).get_page(request.GET.get('page'))
    page.object_list = list(page.object_list)
    podium = list(players[:3])
    visible_players = {player.pk: player for player in (*podium, *page.object_list)}
    for player in visible_players.values():
        team_names = {
            entry.team.name for entry in player.team_roster_entries.all()
        }
        team_names.update(
            membership.team.name
            for membership in player.owner.team_memberships.all()
            if membership.status == TeamMembership.Status.ACTIVE
        )
        player.leaderboard_teams = sorted(team_names)
    start_position = (page.number - 1) * page.paginator.per_page
    for position, player in enumerate(page.object_list, start=start_position + 1):
        player.leaderboard_position = position

    return render(request, 'community/player_leaderboard.html', {
        'page': page,
        'podium': podium,
        'query': query,
        'role': role,
        'rank': rank,
        'server': server,
        'team_id': team_id,
        'sort': sort,
        'roles': ROLES,
        'ranks': RANK_VALUES,
        'teams': Team.objects.filter(
            Q(roster_entries__player__owner__isnull=False, roster_entries__player__available_for_team=True)
            | Q(
                memberships__user__player_profile__available_for_team=True,
                memberships__status=TeamMembership.Status.ACTIVE,
            )
        ).distinct().order_by('name'),
        'total_players': page.paginator.count,
    })


@login_required
def hero_catalog(request):
    heroes = Hero.objects.filter(is_active=True)
    query = request.GET.get('q', '').strip()
    lane = request.GET.get('lane', '').strip()
    sort = request.GET.get('sort', 'name')
    if query:
        heroes = heroes.filter(name__icontains=query)
    lanes = tuple(
        heroes.model.objects.filter(is_active=True)
        .exclude(role='')
        .order_by('role')
        .values_list('role', flat=True)
        .distinct()
    )
    if lane in lanes:
        heroes = heroes.filter(role=lane)
    else:
        lane = ''
    if sort == 'lane':
        heroes = heroes.order_by('role', 'name')
    else:
        sort = 'name'
        heroes = heroes.order_by('name')
    page = Paginator(heroes, 24).get_page(request.GET.get('page'))
    return render(request, 'community/hero_catalog.html', {
        'page': page,
        'query': query,
        'lane': lane,
        'lanes': lanes,
        'sort': sort,
    })


@login_required
def hero_detail(request, hero_id):
    hero = get_object_or_404(Hero, pk=hero_id, is_active=True)
    return render(request, 'community/hero_detail.html', {'hero': hero})


@login_required
def account_settings(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    form = AccountSettingsForm(
        request.POST if request.method == 'POST' else None,
        user=request.user,
        profile=profile,
    )
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Account settings updated.')
        return redirect('account-settings')
    return render(request, 'community/account_settings.html', {'form': form})


@login_required
def notifications(request):
    managed_teams = Team.objects.filter(
        Q(owner=request.user) | Q(
            memberships__user=request.user,
            memberships__status=TeamMembership.Status.ACTIVE,
            memberships__role__in=(TeamMembership.Role.CAPTAIN, TeamMembership.Role.MANAGER),
        )
    ).distinct()
    return render(request, 'community/notifications.html', {
        'team_requests': TeamMembership.objects.filter(
            team__in=managed_teams,
            status=TeamMembership.Status.REQUESTED,
        ).select_related('team', 'user'),
        'membership_updates': TeamMembership.objects.filter(
            user=request.user,
        ).exclude(team__owner=request.user).select_related('team'),
        'tournament_requests': TournamentEntry.objects.filter(
            tournament__organizer=request.user,
            status=TournamentEntry.Status.REQUESTED,
        ).select_related('team', 'tournament'),
        'tournament_updates': TournamentEntry.objects.filter(
            team__in=managed_teams,
        ).exclude(status=TournamentEntry.Status.REQUESTED).select_related('team', 'tournament'),
    })


@login_required
def teams(request):
    form = TeamForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        if not profile.is_team_staff:
            messages.error(request, 'A team captain, manager, or coach role is required to create a team.')
            return redirect('teams')
        try:
            with transaction.atomic():
                team = form.save(commit=False)
                team.owner = request.user
                team.save()
                TeamMembership.objects.create(
                    team=team, user=request.user,
                    role=TeamMembership.Role.CAPTAIN,
                    status=TeamMembership.Status.ACTIVE,
                )
        except IntegrityError:
            logger.exception('Unable to create team for user %s', request.user.pk)
            form.add_error('name', 'A team with that name already exists.')
        else:
            messages.success(request, 'Your team is ready. You are its captain.')
            return redirect('team-detail', team_id=team.pk)
    return render(request, 'community/teams.html', {
        'form': form,
        'teams': Team.objects.filter(recruiting=True).select_related('owner').prefetch_related('memberships'),
        'my_teams': Team.objects.filter(
            Q(owner=request.user) | Q(memberships__user=request.user, memberships__status=TeamMembership.Status.ACTIVE)
        ).distinct(),
        'can_create_team': UserProfile.objects.filter(user=request.user, is_team_staff=True).exists(),
    })


@login_required
def team_edit(request, team_id):
    team = get_object_or_404(Team, pk=team_id)
    if team.owner_id != request.user.pk:
        return redirect('team-detail', team_id=team.pk)
    form = TeamForm(request.POST if request.method == 'POST' else None, instance=team)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Team details updated.')
        return redirect('team-detail', team_id=team.pk)
    return render(request, 'community/team_edit.html', {'team': team, 'form': form})


@login_required
def team_detail(request, team_id):
    team = get_object_or_404(Team.objects.select_related('owner').prefetch_related(
        'memberships__user', 'memberships__user__player_profile',
        'roster_entries__player',
    ), pk=team_id)
    membership = TeamMembership.objects.filter(team=team, user=request.user).first()
    manages = team.owner_id == request.user.pk or TeamMembership.objects.filter(
        team=team, user=request.user, status=TeamMembership.Status.ACTIVE,
        role__in=(TeamMembership.Role.CAPTAIN, TeamMembership.Role.MANAGER),
    ).exists()
    add_player_form = TeamPlayerAddForm(team=team)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'request_join':
            if team.recruiting and (membership is None or membership.status == TeamMembership.Status.DECLINED):
                if membership:
                    membership.status = TeamMembership.Status.REQUESTED
                    membership.save(update_fields=('status',))
                else:
                    TeamMembership.objects.create(team=team, user=request.user)
                messages.success(request, 'Your request to join was sent.')
            else:
                messages.error(request, 'This team is not accepting your request.')
        elif action == 'add_player' and manages:
            add_player_form = TeamPlayerAddForm(request.POST, team=team)
            if add_player_form.is_valid():
                player = add_player_form.cleaned_data['player']
                if player.owner_id is None:
                    _, created = TeamRosterEntry.objects.get_or_create(
                        team=team,
                        player=player,
                        defaults={'added_by': request.user},
                    )
                    if created:
                        messages.success(request, f'{player.ign} was added to the roster.')
                    else:
                        messages.error(request, 'That player is already on the roster.')
                    return redirect('team-detail', team_id=team.pk)
                membership, created = TeamMembership.objects.get_or_create(
                    team=team,
                    user=player.owner,
                    defaults={
                        'role': TeamMembership.Role.PLAYER,
                        'status': TeamMembership.Status.ACTIVE,
                    },
                )
                if created:
                    messages.success(request, f'{player.ign} was added to the roster.')
                    return redirect('team-detail', team_id=team.pk)
                if membership.status == TeamMembership.Status.DECLINED:
                    membership.role = TeamMembership.Role.PLAYER
                    membership.status = TeamMembership.Status.ACTIVE
                    membership.save(update_fields=('role', 'status'))
                    messages.success(request, f'{player.ign} was added to the roster.')
                    return redirect('team-detail', team_id=team.pk)
                messages.error(request, 'That player already has a team request or membership.')
                return redirect('team-detail', team_id=team.pk)
            messages.error(request, 'Choose an available player profile to add to the roster.')
        elif action == 'review_membership' and manages:
            target = get_object_or_404(TeamMembership, pk=request.POST.get('membership_id'), team=team)
            decision = request.POST.get('decision')
            if target.status == TeamMembership.Status.REQUESTED and decision in ('accept', 'decline'):
                target.status = (
                    TeamMembership.Status.ACTIVE
                    if decision == 'accept'
                    else TeamMembership.Status.DECLINED
                )
                target.save(update_fields=('status',))
                messages.success(request, 'Membership request updated.')
        elif action == 'remove_member' and manages:
            target = get_object_or_404(TeamMembership, pk=request.POST.get('membership_id'), team=team)
            if target.user_id != team.owner_id:
                target.delete()
                messages.success(request, 'Team member removed.')
        elif action == 'remove_roster_entry' and manages:
            target = get_object_or_404(
                TeamRosterEntry,
                pk=request.POST.get('roster_entry_id'),
                team=team,
            )
            target.delete()
            messages.success(request, 'Player record removed from the team roster.')
        elif action == 'update_role' and manages:
            target = get_object_or_404(
                TeamMembership, pk=request.POST.get('membership_id'), team=team,
                status=TeamMembership.Status.ACTIVE,
            )
            role = request.POST.get('role')
            can_assign_role = (
                target.user_id != team.owner_id and (
                    team.owner_id == request.user.pk
                    or (role not in (TeamMembership.Role.CAPTAIN, TeamMembership.Role.MANAGER)
                    and membership and membership.role == TeamMembership.Role.CAPTAIN)
                )
            )
            if role in TeamMembership.Role.values and can_assign_role:
                target.role = role
                target.save(update_fields=('role',))
                messages.success(request, 'Team responsibility updated.')
            else:
                messages.error(request, 'You cannot assign that team responsibility.')
        elif action == 'leave' and membership and request.user.pk != team.owner_id:
            membership.delete()
            messages.success(request, 'You left the team.')
        elif action == 'disband' and team.owner_id == request.user.pk:
            team.delete()
            messages.success(request, 'Team disbanded.')
            return redirect('teams')
        else:
            messages.error(request, 'You are not allowed to perform that team action.')
        if action != 'add_player' or not manages or add_player_form.is_valid():
            return redirect('team-detail', team_id=team.pk)
    return render(request, 'community/team_detail.html', {
        'team': team, 'membership': membership, 'manages': manages,
        'add_player_form': add_player_form,
        'available_player_count': add_player_form.fields['player'].queryset.count(),
        'active_member_count': team.memberships.filter(status=TeamMembership.Status.ACTIVE).count(),
        'roster_entry_count': team.roster_entries.count(),
        'accepted_entries': team.tournament_entries.filter(status=TournamentEntry.Status.ACCEPTED).select_related('tournament'),
    })


@login_required
def tournaments(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    form = TournamentForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST':
        if not profile.is_tournament_organizer:
            messages.error(request, 'Select the tournament organizer role at account creation to create events.')
        elif form.is_valid():
            tournament = form.save(commit=False)
            tournament.organizer = request.user
            tournament.save()
            messages.success(request, 'Tournament created.')
            return redirect('tournament-detail', tournament_id=tournament.pk)
    return render(request, 'community/tournaments.html', {
        'form': form,
        'can_organize': profile.is_tournament_organizer,
        'tournaments': Tournament.objects.select_related('organizer').prefetch_related('entries'),
    })


@login_required
def tournament_detail(request, tournament_id):
    tournament = get_object_or_404(
        Tournament.objects.select_related('organizer').prefetch_related('entries__team'),
        pk=tournament_id,
    )
    manages = tournament.organizer_id == request.user.pk
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'register':
            team = get_object_or_404(Team, pk=request.POST.get('team_id'))
            can_manage_team = team.owner_id == request.user.pk or TeamMembership.objects.filter(
                team=team, user=request.user, status=TeamMembership.Status.ACTIVE,
                role__in=(TeamMembership.Role.CAPTAIN, TeamMembership.Role.MANAGER),
            ).exists()
            if not can_manage_team:
                messages.error(request, 'Only the team owner, captain, or manager can register it.')
            elif tournament.registration_deadline <= timezone.now() or tournament.status != Tournament.Status.UPCOMING:
                messages.error(request, 'Registration for this tournament is closed.')
            else:
                entry, created = TournamentEntry.objects.get_or_create(tournament=tournament, team=team)
                if created or entry.status == TournamentEntry.Status.DECLINED:
                    if not created:
                        entry.status = TournamentEntry.Status.REQUESTED
                        entry.save(update_fields=('status',))
                    messages.success(request, 'Team registration request submitted.')
                else:
                    messages.error(request, 'This team already has an entry for the tournament.')
        elif action == 'review_entry' and manages:
            entry = get_object_or_404(TournamentEntry, pk=request.POST.get('entry_id'), tournament=tournament)
            decision = request.POST.get('decision')
            if decision in ('accept', 'decline'):
                entry.status = (
                    TournamentEntry.Status.ACCEPTED
                    if decision == 'accept'
                    else TournamentEntry.Status.DECLINED
                )
                entry.save(update_fields=('status',))
                messages.success(request, 'Tournament entry updated.')
            else:
                messages.error(request, 'Choose a valid entry decision.')
        else:
            messages.error(request, 'You are not allowed to perform that tournament action.')
        return redirect('tournament-detail', tournament_id=tournament.pk)
    manageable_teams = Team.objects.filter(
        Q(owner=request.user) | Q(memberships__user=request.user, memberships__status=TeamMembership.Status.ACTIVE,
                                  memberships__role__in=(TeamMembership.Role.CAPTAIN, TeamMembership.Role.MANAGER))
    ).distinct()
    existing_entry_ids = tournament.entries.exclude(
        status=TournamentEntry.Status.DECLINED,
    ).values_list('team_id', flat=True)
    return render(request, 'community/tournament_detail.html', {
        'tournament': tournament, 'manages': manages,
        'manageable_teams': manageable_teams.exclude(pk__in=existing_entry_ids),
        'now': timezone.now(),
    })


@login_required
def tournament_edit(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)
    if tournament.organizer_id != request.user.pk:
        return redirect('tournament-detail', tournament_id=tournament.pk)
    form = TournamentForm(request.POST if request.method == 'POST' else None, instance=tournament)
    if request.method == 'POST':
        if request.POST.get('action') == 'delete':
            tournament.delete()
            messages.success(request, 'Tournament deleted.')
            return redirect('tournaments')
        if form.is_valid():
            form.save()
            messages.success(request, 'Tournament updated.')
            return redirect('tournament-detail', tournament_id=tournament.pk)
    return render(request, 'community/tournament_edit.html', {'tournament': tournament, 'form': form})
