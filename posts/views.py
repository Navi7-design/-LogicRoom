from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, PostRating, Category
from django.core.paginator import Paginator
from .forms import CommentForm
from django.db.models import Q
from django.db.models import Avg, Count, Value, FloatField
from django.contrib.auth.decorators import login_required
from django.db.models.functions import Coalesce
from .models import Follow, Notification

def index(request):
    posts = Post.objects.all().order_by("-created_at")

    unread_notifications = 0

    if request.user.is_authenticated:
        unread_notifications = request.user.notifications.filter(
            is_read=False
        ).count()

    context = {
        "posts": posts,
        "unread_notifications": unread_notifications,
    }

    return render(request, "index.html", context)

from django.shortcuts import render

def support_page(request):
    return render(request, "support.html")

def support_page(request):
    return render(request, "support.html")

def create_post(request):
    from .forms import CreatePostForm

    if request.method == "POST":
        form = CreatePostForm(request.POST, request.FILES)
        

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
                

            return redirect("index")

    else:
        form = CreatePostForm()

    context = {
        "form": form,
        "is_edit": False
    }

    return render(request, "create_post.html", context)


def posts_page(request, slug=None):
    search = request.GET.get("search", "").strip()

    posts = Post.objects.all().order_by("-id")
    categories = Category.objects.all()

    active_category = None
    if slug:
        active_category = get_object_or_404(Category, slug=slug)
        posts = posts.filter(category=active_category)

    if search:
        posts = posts.filter(
            Q(title__icontains=search)
            | Q(short_description__icontains=search)
            | Q(content__icontains=search)
            | Q(category__title__icontains=search)
            | Q(author__username__icontains=search)
            | Q(author__email__icontains=search)
        )
    posts = posts.annotate(
        avg_rating=Avg("ratings__value"), rating_count=Count("ratings")
    )

    paginator = Paginator(posts, 5)
    page = request.GET.get("page")
    page_obj = paginator.get_page(page)

    return render(
        request,
        "posts.html",
        {
            "page_obj": page_obj,
            "categories": categories,
            "active_category": active_category,
        },
    )


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all().order_by("-created_at")

    stats = post.ratings.aggregate(avg=Avg("value"), count=Count("id"))

    avg_rating = stats["avg"] or 0
    rating_count = stats["count"]
    user_rating = 0

    if request.user.is_authenticated:
        rating_obj = post.ratings.filter(user=request.user).first()
        if rating_obj:
            user_rating = rating_obj.value

    if request.method == "POST":
        form = CommentForm(request.POST)

        if not request.user.is_authenticated:
            form.add_error(None, "You must be logged in to leave a comment.")

        elif form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()

            return redirect(f"/posts/detail/{post.id}/#comments")

    else:
        form = CommentForm()
    if request.user.is_authenticated:

        Notification.objects.filter(
            post_id=post_id,
            is_read=False
        ).update(is_read=True)

    similar_posts = (
        Post.objects.filter(category=post.category)
        .exclude(id=post.id)
        .annotate(
            rating_count=Count("ratings"),
            avg_rating=Avg("ratings__value"),
        )
        .order_by("-avg_rating")
    )

    return render(
        request,
        "post_detail.html",
        {
            "post": post,
            "comments": comments,
            "form": form,
            "avg_rating": avg_rating,
            "rating_count": rating_count,
            "user_rating": user_rating,
            "similar_posts": similar_posts,
        },
    )


from django.http import JsonResponse
from django.contrib.auth.decorators import login_required


@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True

    return JsonResponse({"liked": liked})


@login_required
def toggle_save(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user in post.saved_by.all():
        post.saved_by.remove(request.user)
        saved = False
    else:
        post.saved_by.add(request.user)
        saved = True

    return JsonResponse({"saved": saved})

from .models import Comment, CommentVote

@login_required

def vote_comment(request, comment_id, value):
    comment = get_object_or_404(Comment, id=comment_id)

    vote, created = CommentVote.objects.get_or_create(
        user=request.user, comment=comment, defaults={"value": value}
    )

    if not created:
        vote.value = value
        vote.save()

    return redirect(reverse("post_detail", args=[comment.post.id]) + "#comments")


from django.urls import reverse

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    post_id = comment.post.id

    if request.user != comment.author:
        return redirect(reverse("post_detail", args=[post_id]) + "#comments")

    if request.method == "POST":
        comment.delete()

    return redirect(reverse("post_detail", args=[post_id]) + "#comments")

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

@login_required
def edit_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk, author=request.user)
    post_id = comment.post.id
    if request.user != comment.author:
        return redirect(reverse("post_detail", args=[post_id]) + "#comments")

    if request.method == "POST":
        comment.text = request.POST.get("text")
        comment.save()

    return redirect(request.META.get("HTTP_REFERER", "/"))
def rate_post(request, post_id, value):
    post = get_object_or_404(Post, id=post_id)

    if request.user.is_authenticated:
        PostRating.objects.update_or_create(
            user=request.user, post=post, defaults={"value": value}
        )

    return redirect(reverse("post_detail", args=[post.id]) + "#rate")


from django.contrib.auth.models import User

@login_required
def profile_view(request, username):

    profile_user = get_object_or_404(
        User.objects.select_related("profile"),
        username=username
    )
    user = request.user


    liked_posts = request.user.liked_posts.all()
    saved_posts = request.user.saved_posts.all()

    posts = (
        Post.objects.filter(author=profile_user)
        .annotate(
            avg_rating=Avg("ratings__value"),
            ratings_count=Count("ratings"),
            comments_count=Count("comments"),
        )
        .order_by("-created_at")
    )

    top_posts = posts.order_by("-avg_rating")[:5]
    ratings_count = sum(p.ratings_count for p in posts)
    comments_count = sum(p.comments_count for p in posts)
    posts_count = posts.count()

    followers_count = profile_user.followers.count()
    following_count = profile_user.following.count()

    is_following = Follow.objects.filter(
        follower=request.user,
        following=profile_user
    ).exists()
    

    if request.method == "POST":

        username_new = request.POST.get("username", "").strip()
        email_new = request.POST.get("email", "").strip()
        bio = request.POST.get("bio", "").strip()

        website = request.POST.get("website", "").strip()
        instagram_url = request.POST.get("instagram_url", "").strip()
        twitter_url = request.POST.get("twitter_url", "").strip()
        youtube_url = request.POST.get("youtube_url", "").strip()
        facebook_url = request.POST.get("facebook_url", "").strip()
        tiktok_url = request.POST.get("tiktok_url", "").strip()
        discord_url = request.POST.get("discord_url", "").strip()
        telegram_url = request.POST.get("telegram_url", "").strip()
        sponsorship_url = request.POST.get("snapchat_url", "").strip()
        twitch_url = request.POST.get("twitch_url", "").strip()

        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()

        if request.FILES.get("avatar"):
            profile_user.profile.avatar = request.FILES["avatar"]

        if User.objects.exclude(id=profile_user.id).filter(username=username_new).exists():
            messages.error(request, "Username is already taken ❌")
            return redirect("profile", username=profile_user.username)

        if User.objects.exclude(id=profile_user.id).filter(email=email_new).exists():
            messages.error(request, "Email is already in use ❌")
            return redirect("profile", username=profile_user.username)

        old_username = profile_user.username

        profile_user.username = username_new
        profile_user.email = email_new
        profile_user.first_name = first_name
        profile_user.last_name = last_name
        profile_user.save()

        profile_user.profile.bio = bio
        profile_user.profile.website = website
        profile_user.profile.instagram_url = instagram_url
        profile_user.profile.twitter_url = twitter_url
        profile_user.profile.youtube_url = youtube_url
        profile_user.profile.facebook_url = facebook_url
        profile_user.profile.tiktok_url = tiktok_url
        profile_user.profile.discord_url = discord_url
        profile_user.profile.telegram_url = telegram_url
        profile_user.profile.snapchat_url = sponsorship_url
        profile_user.profile.twitch_url = twitch_url
        profile_user.profile.save()

        messages.success(request, "Profile saved successfully ✅")

        return redirect("profile", username=username_new)

    return render(request, "profile.html", {
        "profile_user": profile_user,
        "posts": posts,
        "similar_posts": top_posts,
        "ratings_count": ratings_count,
        "comments_count": comments_count,
        "posts_count": posts_count,
        "liked_posts": liked_posts,
        "saved_posts": saved_posts,
        "profile_user": profile_user,
        "followers_count": followers_count,
        "following_count": following_count,
        "is_following": is_following,
    })

@login_required
def check_user_exists(request):
    email = request.GET.get("email")
    username = request.GET.get("username")

    if email:
        exists = User.objects.exclude(id=request.user.id).filter(email=email).exists()
        return JsonResponse({"exists": exists})

    if username:
        exists = User.objects.exclude(id=request.user.id).filter(username=username).exists()
        return JsonResponse({"exists": exists})

    return JsonResponse({"exists": False})

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.author == request.user:
        post.delete()

    return redirect("profile", username=request.user.username)


from .forms import CreatePostForm
from django.http import HttpResponseForbidden


@login_required
def edit_post(request, pk):
    post = get_object_or_404(Post, id=pk)
    if post.author != request.user:
        return redirect("index")

    if request.method == "POST":
        form = CreatePostForm(request.POST, request.FILES, instance=post)

        if form.is_valid():
            form.save()
            return redirect("profile", username=post.author.username)

    else:
        form = CreatePostForm(instance=post)

    return render(request, "create_post.html", {"form": form, "is_edit": True})


from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages


def logout_view(request):
    logout(request)
    messages.success(
        request, "👋 You have successfully logged out. See you again soon!"
    )
    return redirect("login")


@login_required
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)

    if request.user != user_to_follow:

        follow, created = Follow.objects.get_or_create(
            follower=request.user,
            following=user_to_follow
        )

        if not created:
            follow.delete()

    return redirect("profile", username=username)

from django.utils import timezone
from datetime import timedelta
@login_required
def notifications_view(request):
    Notification.objects.filter(
        created_at=timezone.now() - timedelta(days=7)
    ).delete()

    notifications = request.user.notifications.all().order_by("-created_at")

    return render(request, "notifications.html", {
        "notifications": notifications
    })
@login_required
def open_notification(request, notification_id):
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        user=request.user
    )

    notification.is_read = True
    notification.save()

    return redirect("post_detail", post_id=notification.post.id)
@login_required
def delete_notification(request, notification_id):
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        user=request.user
    )

    notification.delete()

    return redirect("notifications")


import json

from django.http import JsonResponse

from django.contrib.auth.decorators import login_required


@login_required
def save_social_link(request):

    if request.method == "POST":

        data = json.loads(request.body)

        field = data.get("field")

        url = data.get("url")

        allowed_fields = [
            "website",
            "instagram_url",
            "facebook_url",
            "telegram_url",
            "youtube_url",
            "tiktok_url",
            "twitter_url",
            "discord_url",
            "twitch_url",
            "sponsorship_url",
        ]

        if field not in allowed_fields:

            return JsonResponse({
                "success": False
            })

        profile = request.user.profile

        setattr(profile, field, url)

        profile.save()

        return JsonResponse({
            "success": True,

            "links": {
                "website": profile.website,
                "instagram_url": profile.instagram_url,
                "facebook_url": profile.facebook_url,
                "telegram_url": profile.telegram_url,
                "youtube_url": profile.youtube_url,
                "tiktok_url": profile.tiktok_url,
                "twitter_url": profile.twitter_url,
                "discord_url": profile.discord_url,
                "twitch_url": profile.twitch_url,
                "sponsorship_url": profile.sponsorship_url,
            }
        })

    return JsonResponse({
        "success": False
    })


from django.shortcuts import get_object_or_404, render
from django.contrib.auth.models import User


def followers_page(request, username):
    profile_user = get_object_or_404(User, username=username)

    followers = User.objects.filter(following__following=profile_user)

    following = User.objects.filter(followers__follower=profile_user)

    return render(
        request,
        "followers.html",
        {
            "profile_user": profile_user,
            "followers": followers,
            "following": following,
        },
    )


