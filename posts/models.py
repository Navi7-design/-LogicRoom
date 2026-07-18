from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from tinymce import models as tinymce_models


class Category(models.Model):
    title = models.CharField(max_length=100, unique=True, null=False, blank=True)
    slug = models.SlugField(max_length=100, unique=True, null=False, blank=True)
    icon = models.TextField(null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.title}"


from django.utils.text import slugify

class Post(models.Model):
    title = models.CharField(max_length=255, unique=True, blank=False, null=False)
    slug = models.SlugField(max_length=100, unique=True, blank=False, null=False)
    short_description = models.TextField(max_length=500, blank=False, null=False)
    content = tinymce_models.HTMLField(blank=False, null=False)
    image = models.ImageField(upload_to="post_images/", null=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="posts"
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, blank=True, related_name="liked_posts")
    saved_by = models.ManyToManyField(User, blank=True, related_name="saved_posts")

    class Meta:
        verbose_name_plural = "Posts"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Post: {self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            num = 1
            while Post.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            self.slug = slug
        super().save(*args, **kwargs)
        
from django.core.exceptions import ValidationError
class Comment(models.Model):
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=1000, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if not self.text or self.text.strip() == "":
            raise ValidationError({"text": "Comment cannot be empty"})

        if len(self.text.strip()) < 3:
            raise ValidationError({"text": "Comment must be at least 3 characters"})

    def save(self, *args, **kwargs):
        self.full_clean()  # викликає clean()
        super().save(*args, **kwargs)

    def total_likes(self):
        return self.votes.filter(value=1).count()

    def total_dislikes(self):
        return self.votes.filter(value=-1).count()

    def __str__(self):
        return f"{self.author} - {self.text[:30]}"

    class Meta:
        ordering = ['-created_at']

class CommentVote(models.Model):
    VALUE_CHOICES = (
        (1, "Like"),
        
        (-1, "Dislike"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="votes")
    value = models.SmallIntegerField(choices=VALUE_CHOICES)

    class Meta:
        unique_together = ("user", "comment")  

class PostRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="ratings")
    value = models.PositiveSmallIntegerField()  

    class Meta:
        unique_together = ("user", "post")
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
class Follow(models.Model):
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following"
    )

    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="followers"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "following")

    def __str__(self):
        return f"{self.follower} -> {self.following}"
    
class Notification(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    post = models.ForeignKey(
        "Post",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    text = models.CharField(max_length=255)

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_emailed = models.BooleanField(default=False)

class NotificationSettings(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    daily_digest = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username

class Donation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def get_level(total):
        if total >= 1500:
            return "whale"
        elif total >= 1000:
            return "legend"
        elif total >= 500:
            return "elite"
        elif total >= 250:
            return "advanced"
        elif total >= 100:
            return "supporter"
        elif total >= 49:
            return "friend"
        elif total >= 10:
            return "new"
        return "visitor"
    
class DigestConfig(models.Model):
    send_hour = models.PositiveSmallIntegerField(
        default=10, help_text="UTC hour to send email notifications (0-23)"
    )
    max_posts_per_author = models.PositiveSmallIntegerField(default=4)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        self.pk = 1
        return super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return f"Send at: {self.send_hour:02d}:00 UTC | max {self.max_posts_per_author} posts/author"