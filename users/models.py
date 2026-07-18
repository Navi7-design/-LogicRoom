
from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    avatar = models.ImageField(
        upload_to="avatars/",
        default="avatars/default.png",
        blank=True
    )

    bio = models.TextField(blank=True, max_length=500)

    website = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    tiktok_url = models.URLField(blank=True)
    discord_url = models.URLField(blank=True)
    telegram_url = models.URLField(blank=True)
    sponsorship_url = models.URLField(blank=True)
    twitch_url = models.URLField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    bonus_donations = models.IntegerField(default=0)
    
    
    def __str__(self):
        return f"{self.user.username}'s profile"