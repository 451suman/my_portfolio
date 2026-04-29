from rest_framework import generics, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Category, Tag, BlogPost, Comment
from .serializers import (
    CategorySerializer,
    TagSerializer,
    BlogPostSerializer,
    BlogPostListSerializer,
    BlogPostCreateUpdateSerializer,
    CommentSerializer,
)


class CategoryListView(generics.ListCreateAPIView):
    """
    List and create blog categories
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticatedOrReadOnly()]


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, and delete blog categories
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = "slug"


class TagListView(generics.ListCreateAPIView):
    """
    List and create tags
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticatedOrReadOnly()]


class TagDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, and delete tags
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = "slug"


class BlogPostListView(generics.ListCreateAPIView):
    """
    List and create blog posts
    """

    queryset = BlogPost.objects.select_related("author", "category").prefetch_related(
        "tags"
    )
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["status", "featured", "category", "tags"]
    search_fields = ["title", "content", "excerpt"]
    ordering_fields = ["published_at", "created_at", "title"]
    ordering = ["-published_at", "-created_at"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return BlogPostCreateUpdateSerializer
        return BlogPostListSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticatedOrReadOnly()]

    def get_queryset(self):
        queryset = super().get_queryset()
        # Only show published posts to non-authenticated users
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(status="published")
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class BlogPostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, and delete blog posts
    """

    queryset = BlogPost.objects.select_related("author", "category").prefetch_related(
        "tags"
    )
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = "slug"

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return BlogPostCreateUpdateSerializer
        return BlogPostSerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticatedOrReadOnly()]

    def get_object(self):
        obj = super().get_object()
        # Check if user has permission to edit
        if (
            self.request.method in ["PUT", "PATCH", "DELETE"]
            and obj.author != self.request.user
        ):
            self.permission_denied(
                self.request, message="You don't have permission to edit this post"
            )
        return obj


class CommentCreateView(generics.CreateAPIView):
    """
    Create comments on blog posts
    """

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        post_id = self.kwargs.get("post_id")
        try:
            post = BlogPost.objects.get(id=post_id)
            serializer.save(post=post)
        except BlogPost.DoesNotExist:
            raise serializers.ValidationError("Invalid post ID")


class CommentCreateSlugView(generics.CreateAPIView):
    """
    Create comments on blog posts using slug (for guest users)
    """

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.AllowAny]  # Allow guest comments

    def perform_create(self, serializer):
        post_slug = self.kwargs.get("slug")
        try:
            post = BlogPost.objects.get(slug=post_slug)
            # Handle guest user data
            if self.request.user.is_authenticated:
                serializer.save(post=post, author=self.request.user)
            else:
                # For guest users, author will be None and we'll use author_name/email from request data
                serializer.save(post=post, author=None)
        except BlogPost.DoesNotExist:
            raise serializers.ValidationError("Invalid post slug")


class CommentListView(generics.ListAPIView):
    """
    List comments for a specific post
    """

    serializer_class = CommentSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        post_id = self.kwargs.get("post_id")
        return (
            Comment.objects.filter(post_id=post_id, is_approved=True)
            .order_by("created_at")
            .select_related("author")
            .prefetch_related("replies")
        )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
def blog_stats_view(request):
    """
    Get blog statistics
    """
    stats = {
        "total_posts": BlogPost.objects.count(),
        "published_posts": BlogPost.objects.filter(status="published").count(),
        "draft_posts": BlogPost.objects.filter(status="draft").count(),
        "total_categories": Category.objects.count(),
        "total_tags": Tag.objects.count(),
        "total_comments": Comment.objects.filter(is_approved=True).count(),
    }

    if request.user.is_authenticated:
        stats["my_posts"] = BlogPost.objects.filter(author=request.user).count()
        stats["my_drafts"] = BlogPost.objects.filter(
            author=request.user, status="draft"
        ).count()
        stats["my_published"] = BlogPost.objects.filter(
            author=request.user, status="published"
        ).count()

    return Response(stats)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
def popular_posts_view(request):
    """
    Get popular blog posts (can be customized based on views, likes, etc.)
    """
    posts = (
        BlogPost.objects.filter(status="published")
        .select_related("author", "category")
        .prefetch_related("tags")[:10]
    )

    serializer = BlogPostListSerializer(posts, many=True, context={"request": request})
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
def posts_by_category_view(request, slug):
    """
    Get posts by category
    """
    try:
        category = Category.objects.get(slug=slug)
        posts = (
            BlogPost.objects.filter(category=category, status="published")
            .select_related("author", "category")
            .prefetch_related("tags")
        )

        serializer = BlogPostListSerializer(
            posts, many=True, context={"request": request}
        )
        return Response(serializer.data)
    except Category.DoesNotExist:
        return Response(
            {"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
def posts_by_tag_view(request, slug):
    """
    Get posts by tag
    """
    try:
        tag = Tag.objects.get(slug=slug)
        posts = (
            BlogPost.objects.filter(tags=tag, status="published")
            .select_related("author", "category")
            .prefetch_related("tags")
        )

        serializer = BlogPostListSerializer(
            posts, many=True, context={"request": request}
        )
        return Response(serializer.data)
    except Tag.DoesNotExist:
        return Response({"error": "Tag not found"}, status=status.HTTP_404_NOT_FOUND)
