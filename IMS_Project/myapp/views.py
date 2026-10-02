import json
import logging

from django.contrib import messages
from django.db.models import Avg
from django.http import JsonResponse
from django.shortcuts import redirect, render

from .forms import PlayerForm
from .models import Player
from .mlbb_api import LookupError, _validate_identifier, lookup_player


logger = logging.getLogger(__name__)


def _json_body(request):
    try:
        data = json.loads(request.body)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


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
        logger.exception('Unexpected error while looking up MLBB player %s/%s', player_id if 'player_id' in locals() else '?', server_id if 'server_id' in locals() else '?')
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


def index(request):
    form = PlayerForm(request.POST if request.method == 'POST' else None)
    duplicate_player = None
    if request.method == 'POST':
        update_existing = request.POST.get('update_existing') == '1'
        submitted_id = request.POST.get('player_id', '').strip()
        submitted_server = request.POST.get('server', '').strip()
        if update_existing and submitted_id.isdecimal() and submitted_server.isdecimal():
            duplicate_player = Player.objects.filter(
                player_id=int(submitted_id), server=int(submitted_server)
            ).first()
            if duplicate_player:
                form = PlayerForm(request.POST, instance=duplicate_player)
        elif submitted_id.isdecimal() and submitted_server.isdecimal():
            duplicate_player = Player.objects.filter(
                player_id=int(submitted_id), server=int(submitted_server)
            ).first()
        if form.is_valid():
            existing = Player.objects.filter(
                player_id=form.cleaned_data['player_id'],
                server=form.cleaned_data['server'],
            ).first()
            if existing and not update_existing:
                duplicate_player = existing
                form.add_error(None, 'This player already exists in the database.')
            elif update_existing and not duplicate_player:
                form.add_error(None, 'This player could not be found. Look it up again before updating.')
            else:
                form.save()
                messages.success(
                    request,
                    'Player updated successfully!' if update_existing else 'Player added successfully!',
                )
                return redirect('index')
        elif duplicate_player:
            form.add_error(None, 'This player already exists in the database.')

    players = Player.objects.all().order_by('ign')
    total_players = players.count()
    avg_win_rate = players.aggregate(avg_win_rate=Avg('win_rate'))['avg_win_rate'] or 0
    highest_player = players.order_by('-highest_stars', 'ign').first()

    context = {
        'players': players,
        'total_players': total_players,
        'avg_win_rate': avg_win_rate,
        'highest_player': highest_player,
        'form': form,
        'open_add_player': request.method == 'POST' and bool(form.errors),
        'duplicate_player': duplicate_player,
    }
    return render(request, 'dashboard.html', context)
