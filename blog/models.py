from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    """
    Blog post categories
    """

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(
        max_length=7, default="#007bff", help_text="Hex color code"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Tag(models.Model):
    """
    Blog post tags for better categorization
    """

    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class BlogPost(models.Model):
    """
    Blog posts with Markdown support
    """

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
        ("archived", "Archived"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="blog_posts"
    )
    content = models.TextField(help_text="Markdown content")
    excerpt = models.CharField(
        max_length=300, blank=True, help_text="Brief description for preview cards"
    )
    featured_image = models.ImageField(upload_to="blog/images/", blank=True, null=True)

    # Categorization
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="posts"
    )
    tags = models.ManyToManyField(Tag, related_name="posts", blank=True)

    # Status and metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    featured = models.BooleanField(default=False)
    estimated_reading_time = models.PositiveIntegerField(
        default=5, help_text="Estimated reading time in minutes"
    )

    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)
    meta_keywords = models.CharField(max_length=200, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["status", "featured"]),
            models.Index(fields=["author"]),
            models.Index(fields=["published_at"]),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("blog:post_detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        # Auto-generate excerpt if not provided
        if not self.excerpt:
            # Take first 300 characters of content (strip markdown)
            plain_content = (
                self.content[:300].replace("#", "").replace("*", "").replace("`", "")
            )
            self.excerpt = (
                plain_content + "..." if len(self.content) > 300 else plain_content
            )

        # Set published_at when status changes to published
        if self.status == "published" and not self.published_at:
            from django.utils import timezone

            self.published_at = timezone.now()

        super().save(*args, **kwargs)

    @property
    def is_published(self):
        return self.status == "published"

    @property
    def word_count(self):
        """Calculate approximate word count"""
        return len(self.content.split())

    @property
    def related_posts(self):
        """Get related posts based on tags and category"""
        related = BlogPost.objects.filter(status="published").exclude(id=self.id)

        # First try to find posts with same tags
        if self.tags.exists():
            related = related.filter(tags__in=self.tags.all()).distinct()

        # If no related posts by tags, try category
        if related.count() == 0 and self.category:
            related = related.filter(category=self.category)

        return related[:3]


class Comment(models.Model):
    """
    Comments on blog posts
    """

    post = models.ForeignKey(
        BlogPost, on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blog_comments",
        null=True,
        blank=True,
    )

    # For non-registered users
    author_name = models.CharField(max_length=100, blank=True)
    author_email = models.EmailField(blank=True)
    author_website = models.URLField(blank=True)

    content = models.TextField()
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )

    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        author_name = self.author_name or (
            self.author.username if self.author else "Anonymous"
        )
        return f"Comment by {author_name} on {self.post.title}"

    @property
    def display_name(self):
        if self.author:
            return self.author.get_full_name() or self.author.username
        return self.author_name

    @property
    def is_reply(self):
        return self.parent is not None
