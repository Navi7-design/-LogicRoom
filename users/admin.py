from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display=("user", "website", "instagram_url", "twitter_url")
    search_fields = ("user__username", "user__email", "bio", "website")
    autocomplete_fields = ("user",)
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]
    date_hierarchy = "created_at"
    list_filter = ["created_at", "updated_at"]