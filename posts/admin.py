from django.contrib import admin
from .models import (
    Category,
    Tag,
    Post,
    DigestConfig,
    Notification,
    NotificationSettings,
    Donation,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["title", "created_at"]
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ["title"]
    list_filter = ["created_at"]
    readonly_fields = ["created_at"]
    ordering = ["-created_at"]
    # date_hierarchy = "created_at"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]
    ordering = ["name"]


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "short_description",
        "author",
        "category__title",
        "created_at",
    ]
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ["title", "short_description", "content","author__username"]
    list_filter = ["category__title", "created_at", "updated_at"]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]
    date_hierarchy = "created_at"
    autocomplete_fields = ["category","author"]

from .models import DigestConfig
@admin.register(DigestConfig)
class DigestConfigAdmin(admin.ModelAdmin):
    list_display = ("send_hour", "max_posts_per_author", "is_active")

    def has_add_permission(self, request):
        return not DigestConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
    
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "text", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("user__username", "text")


@admin.register(NotificationSettings)
class NotificationSettingsAdmin(admin.ModelAdmin):
    list_display = ("user", "daily_digest")


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "created_at")
    search_fields = ("user__username",)