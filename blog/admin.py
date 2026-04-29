from django.contrib import admin
from .models import Category, Tag, BlogPost, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "description", "color", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["name", "description"]
    prepopulated_fields = {"slug": ("name",)}
    ordering = ["name"]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}
    ordering = ["name"]


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1
    readonly_fields = ["created_at"]
    fields = [
        "author",
        "author_name",
        "author_email",
        "content",
        "is_approved",
        "created_at",
    ]


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "slug",
        "author",
        "status",
        "featured",
        "category",
        "published_at",
        "created_at",
    ]
    list_filter = ["status", "featured", "category", "published_at", "created_at"]
    search_fields = ["title", "content", "excerpt"]
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ["tags"]
    inlines = [CommentInline]
    ordering = ["-published_at", "-created_at"]

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("title", "slug", "author", "status", "featured")},
        ),
        ("Content", {"fields": ("content", "excerpt", "featured_image")}),
        ("Classification", {"fields": ("category", "tags")}),
        (
            "Metadata",
            {
                "fields": (
                    "estimated_reading_time",
                    "meta_title",
                    "meta_description",
                    "meta_keywords",
                    "published_at",
                )
            },
        ),
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("author", "category")
            .prefetch_related("tags")
        )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["post", "author", "author_name", "is_approved", "created_at"]
    list_filter = ["is_approved", "created_at"]
    search_fields = ["content", "author_name", "author_email"]
    ordering = ["-created_at"]

    fieldsets = (
        ("Comment Information", {"fields": ("post", "content", "is_approved")}),
        (
            "Author Information",
            {"fields": ("author", "author_name", "author_email", "author_website")},
        ),
        ("Relations", {"fields": ("parent",)}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("post", "author", "parent")
