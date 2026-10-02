from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/player-lookup/', views.player_lookup, name='player_lookup'),
]
