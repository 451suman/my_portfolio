from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    # Blog posts
    path("posts/", views.BlogPostListView.as_view(), name="post_list"),
    path("posts/popular/", views.popular_posts_view, name="popular_posts"),
    path("posts/<slug:slug>/", views.BlogPostDetailView.as_view(), name="post_detail"),
    path(
        "posts/category/<slug:slug>/",
        views.posts_by_category_view,
        name="posts_by_category",
    ),
    path("posts/tag/<slug:slug>/", views.posts_by_tag_view, name="posts_by_tag"),
    # Categories
    path("categories/", views.CategoryListView.as_view(), name="category_list"),
    path(
        "categories/<slug:slug>/",
        views.CategoryDetailView.as_view(),
        name="category_detail",
    ),
    # Tags
    path("tags/", views.TagListView.as_view(), name="tag_list"),
    path("tags/<slug:slug>/", views.TagDetailView.as_view(), name="tag_detail"),
    # Comments
    path(
        "posts/<int:post_id>/comments/",
        views.CommentListView.as_view(),
        name="comment_list",
    ),
    path(
        "posts/<int:post_id>/comments/create/",
        views.CommentCreateView.as_view(),
        name="comment_create",
    ),
    path(
        "posts/<slug:slug>/comments/create/",
        views.CommentCreateSlugView.as_view(),
        name="comment_create_slug",
    ),
    # Statistics
    path("stats/", views.blog_stats_view, name="blog_stats"),
]
