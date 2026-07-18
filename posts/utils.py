from .models import Follow
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.template.loader import render_to_string
import urllib.parse


def notify_followers(post):
    followers = Follow.objects.filter(following=post.author)

    post_url = settings.SITE_URL + reverse("post_detail", args=[post.id])

    subject = f"✨ {post.author.username} just dropped something new!"

    author_profile = getattr(post.author, "profile", None)

    if author_profile and author_profile.avatar:
        avatar_url = f"{settings.SITE_URL.rstrip('/')}{author_profile.avatar.url}"
    else:
        avatar_url = (
            "https://ui-avatars.com/api/?name="
            f"{urllib.parse.quote(post.author.username)}"
        )

    context = {
        "post": post,
        "post_url": post_url,
        "avatar_url": avatar_url,
    }

    html_message = render_to_string("email.html", context)

    plain_message = f"{post.author.username} posted: {post.title}\n{post_url}"

    for follow in followers:
        email = follow.follower.email

        if email:
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False,
            )