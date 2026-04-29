from rest_framework import generics, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from .models import Category, Skill, Project, ProjectImage, Experience
from .serializers import (
    CategorySerializer,
    SkillSerializer,
    ProjectSerializer,
    ProjectListSerializer,
    ProjectCreateUpdateSerializer,
    ExperienceSerializer,
    ExperienceCreateUpdateSerializer,
)


class CategoryListView(generics.ListCreateAPIView):
    """
    List and create project categories
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
    Retrieve, update, and delete project categories
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = "slug"


class SkillListView(generics.ListCreateAPIView):
    """
    List and create skills
    """

    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["category"]
    search_fields = ["name"]
    ordering_fields = ["name", "proficiency_level", "created_at"]
    ordering = ["name"]

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticatedOrReadOnly()]


class SkillDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, and delete skills
    """

    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = "slug"


class ProjectListView(generics.ListCreateAPIView):
    """
    List and create projects
    """

    queryset = Project.objects.select_related("owner", "category").prefetch_related(
        "skills", "images"
    )
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["status", "featured", "category", "skills"]
    search_fields = ["title", "description", "short_description"]
    ordering_fields = ["created_at", "updated_at", "title", "start_date"]
    ordering = ["-featured", "-created_at"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ProjectCreateUpdateSerializer
        return ProjectListSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticatedOrReadOnly()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, and delete projects
    """

    queryset = Project.objects.select_related("owner", "category").prefetch_related(
        "skills", "images"
    )
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = "slug"

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return ProjectCreateUpdateSerializer
        return ProjectSerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticatedOrReadOnly()]

    def get_object(self):
        obj = super().get_object()
        # Check if user has permission to edit
        if (
            self.request.method in ["PUT", "PATCH", "DELETE"]
            and obj.owner != self.request.user
        ):
            self.permission_denied(
                self.request, message="You don't have permission to edit this project"
            )
        return obj


class UserProjectsView(generics.ListAPIView):
    """
    List projects for a specific user
    """

    serializer_class = ProjectListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["status", "featured", "category"]
    search_fields = ["title", "description", "short_description"]
    ordering_fields = ["created_at", "updated_at", "title"]
    ordering = ["-featured", "-created_at"]

    def get_queryset(self):
        username = self.kwargs["username"]
        return (
            Project.objects.filter(owner__username=username, status="completed")
            .select_related("owner", "category")
            .prefetch_related("skills", "images")
        )


class FeaturedProjectsView(generics.ListAPIView):
    """
    List featured projects
    """

    serializer_class = ProjectListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = (
        Project.objects.filter(featured=True, status="completed")
        .select_related("owner", "category")
        .prefetch_related("skills", "images")
    )
    ordering = ["-created_at"]


class ExperienceListView(generics.ListCreateAPIView):
    """
    List and create work experience
    """

    serializer_class = ExperienceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Experience.objects.filter(user=self.request.user)
            .select_related("user")
            .prefetch_related("skills_used")
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ExperienceCreateUpdateSerializer
        return ExperienceSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ExperienceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, and delete work experience
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Experience.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return ExperienceCreateUpdateSerializer
        return ExperienceSerializer


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
def portfolio_stats_view(request, username=None):
    """
    Get portfolio statistics for a user
    """
    from django.contrib.auth import get_user_model

    User = get_user_model()

    if username:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
    else:
        user = request.user

    stats = {
        "total_projects": user.projects.count(),
        "completed_projects": user.projects.filter(status="completed").count(),
        "featured_projects": user.projects.filter(featured=True).count(),
        "total_skills": Skill.objects.filter(projects__owner=user).distinct().count(),
        "total_experience": user.experiences.count(),
        "current_jobs": user.experiences.filter(is_current_job=True).count(),
        "blog_posts": user.blog_posts.filter(status="published").count(),
    }

    return Response(stats)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
def skills_by_category_view(request):
    """
    Get skills grouped by category
    """
    skills_by_category = {}
    categories = Skill.objects.values_list("category", flat=True).distinct()

    for category in categories:
        skills = Skill.objects.filter(category=category).order_by("name")
        skills_by_category[category] = SkillSerializer(skills, many=True).data

    return Response(skills_by_category)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def toggle_project_featured_view(request, slug):
    """
    Toggle project featured status
    """
    try:
        project = Project.objects.get(slug=slug, owner=request.user)
        project.featured = not project.featured
        project.save()

        return Response(
            {
                "featured": project.featured,
                "message": f"Project {'featured' if project.featured else 'unfeatured'} successfully",
            }
        )
    except Project.DoesNotExist:
        return Response(
            {"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND
        )
