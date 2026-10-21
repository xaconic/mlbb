from django.contrib import admin

from .models import Hero, Player, Team, TeamMembership, Tournament, TournamentEntry, UserProfile


@admin.register(Hero)
class HeroAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('name',)


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('ign', 'owner', 'main_role', 'current_rank', 'available_for_team')
    list_filter = ('main_role', 'available_for_team')
    search_fields = ('ign', 'owner__username', 'player_id')
    exclude = ('main_heroes',)

    def has_add_permission(self, request):
        return False


admin.site.register((Team, TeamMembership, Tournament, TournamentEntry, UserProfile))