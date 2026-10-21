from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/login/', views.PlayerLoginView.as_view(), name='login'),
    path('accounts/signup/', views.signup, name='signup'),
    path('accounts/logout/', views.signout, name='logout'),
    path(
        'accounts/password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='registration/password_reset_form.html',
            email_template_name='registration/password_reset_email.html',
            subject_template_name='registration/password_reset_subject.txt',
            success_url=reverse_lazy('password-reset-done'),
        ),
        name='password-reset',
    ),
    path(
        'accounts/password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),
        name='password-reset-done',
    ),
    path(
        'accounts/password-change/',
        auth_views.PasswordChangeView.as_view(
            template_name='registration/password_change_form.html',
            success_url=reverse_lazy('account-settings'),
        ),
        name='password-change',
    ),
    path(
        'accounts/reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='registration/password_reset_confirm.html',
            success_url=reverse_lazy('password-reset-complete'),
        ),
        name='password-reset-confirm',
    ),
    path(
        'accounts/reset/complete/',
        auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
        name='password-reset-complete',
    ),
    path('api/player-lookup/', views.player_lookup, name='player_lookup'),
    path('heroes/', views.hero_catalog, name='hero-catalog'),
    path('heroes/<int:hero_id>/', views.hero_detail, name='hero-detail'),
    path('leaderboard/', views.player_leaderboard, name='player-leaderboard'),
    path('profile/', views.player_profile, name='player-profile'),
    path('account/', views.account_settings, name='account-settings'),
    path('notifications/', views.notifications, name='notifications'),
    path('players/', views.player_discovery, name='player-discovery'),
    path('teams/', views.teams, name='teams'),
    path('teams/<int:team_id>/', views.team_detail, name='team-detail'),
    path('teams/<int:team_id>/edit/', views.team_edit, name='team-edit'),
    path('tournaments/', views.tournaments, name='tournaments'),
    path('tournaments/<int:tournament_id>/', views.tournament_detail, name='tournament-detail'),
    path('tournaments/<int:tournament_id>/edit/', views.tournament_edit, name='tournament-edit'),
]
