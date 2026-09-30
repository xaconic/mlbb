from django.contrib import messages
from django.db.models import Avg
from django.shortcuts import redirect, render

from .forms import PlayerForm
from .models import Player


def index(request):
    form = PlayerForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Player added successfully!')
            return redirect('index')

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
        'open_add_player': request.method == 'POST' and form.errors,
    }
    return render(request, 'dashboard.html', context)