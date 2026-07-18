from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Post, Follow, Notification
from .utils import notify_followers


@receiver(post_save, sender=Post)
def post_created(sender, instance, created, **kwargs):
    if not created:
        return
    #notify_followers(instance)

    followers = Follow.objects.filter(following=instance.author)

    notifications = [
        Notification(
            user=follow.follower,
            post=instance,
            text=f"{instance.author.username} created a new post"
        )
        for follow in followers
    ]

    Notification.objects.bulk_create(notifications)