from django.contrib import admin
from .models import Player, Profile
from django.contrib.auth.models import User

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("number", "name", "position", "year")
    search_fields = ("name", "position", "year")


class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "user_email", "is_player")
    list_filter = ("role",)
    search_fields = ("user__username", "user__email", "role")

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = "Email"

    def is_player(self, obj):
        return obj.role == "player"
    is_player.boolean = True


admin.site.register(Profile, ProfileAdmin)