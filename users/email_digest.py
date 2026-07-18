import logging
from datetime import timedelta
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from posts.models import Notification
from posts.models import DigestConfig
logger = logging.getLogger(__name__)


def send_daily_notifications(force=False):
    config = DigestConfig.get()

    if not config.is_active:
        logger.info("Email notifications digest inactive - skipping!")
        return 0

    now = timezone.now()

    if not force and now.hour != config.send_hour:
        logger.info(f"Hour {now.hour} != send_hour {config.send_hour} - skipping!")
        return 0

    since = now - timedelta(hours=24)

    user_ids = (
        Notification.objects.filter(is_emailed=False, created_at__gte=since)
        .values_list("user_id", flat=True)
        .distinct()
    )

    if not user_ids:
        logger.info("No pending notifications - nothing to send!")
        return 0

    send_count = 0

    for user in User.objects.filter(id__in=user_ids).only("email", "username"):
        if not user.email:
            continue

        notifications = (
            Notification.objects.filter(
                user=user,
                is_emailed=False,
                created_at__gte=since,
            )
            .select_related("post", "post__author", "post__category")
            .order_by("post__author_id", "-created_at")
        )

        digest_data = {}
        for n in notifications:
            if not n.post:
                continue
            author = n.post.author
            if author not in digest_data:
                digest_data[author] = []
            if len(digest_data[author]) < config.max_posts_per_author:
                digest_data[author].append(n.post)

        if not digest_data:
            continue

        context = {
            "recipient": user,
            "digest_data": digest_data,
            "site_url": settings.SITE_URL,
            "date": now.strftime("%B %d, %Y"),
        }

        html_body = render_to_string("emails/digest.html", context)
        text_body = (
            f"Hi {user.username},\n\n"
            + "\n".join(
                f"• {post.title} — {settings.SITE_URL}/posts/{post.slug}/"
                for posts in digest_data.values()
                for post in posts
            )
            + f"\n\nManage subscriptions: {settings.SITE_URL}/profile/{user.username}/"
        )

        email = EmailMultiAlternatives(
            subject=f"BlogApp daily digest — {now.strftime('%b %d')}",
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.attach_alternative(html_body, "text/html")

        try:
            email.send()
            notifications.update(is_emailed=True)
            send_count += 1
            logger.info(f"Digest sent → {user.email}")
        except Exception as e:
            logger.error(f"Failed to send to {user.email}: {e}")

    return send_count
