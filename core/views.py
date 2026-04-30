from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.views.generic import TemplateView, DetailView, UpdateView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from portfolio.models import Project, Category, Skill
from blog.models import BlogPost
from accounts.models import Profile
from django.contrib import messages

User = get_user_model()


class HomeView(TemplateView):
    """
    Home page with hero section and featured content
    """

    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            # Get featured projects
            context["featured_projects"] = (
                Project.objects.filter(featured=True, status="completed")
                .select_related("owner", "category")
                .prefetch_related("skills")[:6]
            )
        except Exception:
            context["featured_projects"] = []

        try:
            # Get latest blog posts
            context["latest_posts"] = BlogPost.objects.filter(
                status="published"
            ).select_related("author", "category")[:3]
        except Exception:
            context["latest_posts"] = []

        try:
            # Get skills for display
            skills = Skill.objects.all().order_by("name")[:12]
            context["skills"] = skills
        except Exception:
            context["skills"] = []

        # Get main user profile for display (always show super admin profile)
        try:
            from django.contrib.auth import get_user_model

            User = get_user_model()
            superuser = User.objects.get(is_superuser=True)
            context["profile_user"] = superuser
            context["user_profile"] = getattr(superuser, "profile", None)
        except User.DoesNotExist:
            context["profile_user"] = None
            context["user_profile"] = None
        except Exception:
            context["profile_user"] = None
            context["user_profile"] = None

        try:
            # Get social media links
            from portfolio.models import SocialLink

            links = SocialLink.objects.filter(is_active=True).order_by("display_order")
            context["social_links"] = links
        except Exception:
            context["social_links"] = []

        return context


class AboutView(TemplateView):
    """
    About page with personal information and experience
    """

    template_name = "core/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            # Get main user profile from database
            from accounts.models import Profile

            main_user = User.objects.filter(is_superuser=True).first()
            if main_user:
                try:
                    # Get profile from Profile database
                    context["profile"] = Profile.objects.get(user=main_user)
                except Profile.DoesNotExist:
                    # Create profile if it doesn't exist
                    context["profile"] = Profile.objects.create(user=main_user)

                try:
                    context["experiences"] = main_user.experiences.all().order_by(
                        "-start_date"
                    )
                except Exception:
                    context["experiences"] = []

                try:
                    context["skills"] = Skill.objects.all().order_by("name")
                except Exception:
                    context["skills"] = []
            else:
                context["profile"] = None
                context["experiences"] = []
                context["skills"] = []
        except Exception:
            context["profile"] = None
            context["experiences"] = []
            context["skills"] = []

        return context


class ProjectsView(TemplateView):
    """
    Projects listing page
    """

    template_name = "core/projects.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            # Get all completed projects
            context["projects"] = (
                Project.objects.filter(status="completed")
                .select_related("owner", "category")
                .prefetch_related("skills")
            )
        except Exception:
            context["projects"] = []

        try:
            # Get categories for filtering
            context["categories"] = Category.objects.all()
        except Exception:
            context["categories"] = []

        try:
            # Get skills for filtering
            context["skills"] = Skill.objects.all()
        except Exception:
            context["skills"] = []

        return context


class ProjectDetailView(DetailView):
    """
    Individual project detail page
    """

    model = Project
    template_name = "core/project_detail.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        """Ensure we only get projects with slugs"""
        return Project.objects.filter(slug__isnull=False).exclude(slug="")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            # Get project images
            context["images"] = self.object.images.all().order_by("order")
        except Exception:
            context["images"] = []

        try:
            # Get related projects
            if self.object.category:
                context["related_projects"] = Project.objects.filter(
                    category=self.object.category, status="completed"
                ).exclude(id=self.object.id)[:3]
            else:
                context["related_projects"] = Project.objects.filter(
                    status="completed"
                ).exclude(id=self.object.id)[:3]
        except Exception:
            context["related_projects"] = []

        return context

    def get_object(self, queryset=None):
        """Override to handle missing slugs gracefully"""
        if queryset is None:
            queryset = self.get_queryset()

        slug = self.kwargs.get(self.slug_url_kwarg)
        if not slug:
            raise Http404("No slug provided")

        try:
            obj = queryset.get(slug=slug)
        except Project.DoesNotExist:
            raise Http404("Project not found")
        return obj


class BlogView(TemplateView):
    """
    Blog listing page
    """

    template_name = "core/blog.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            # Get published blog posts
            context["posts"] = (
                BlogPost.objects.filter(status="published")
                .select_related("author", "category")
                .prefetch_related("tags")
            )
        except Exception:
            context["posts"] = []

        try:
            # Get categories
            context["categories"] = Category.objects.all()
        except Exception:
            context["categories"] = []

        return context


class BlogDetailView(DetailView):
    """
    Individual blog post detail page
    """

    model = BlogPost
    template_name = "core/blog_detail.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        """Only show published posts to non-authenticated users"""
        queryset = super().get_queryset()
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(status="published")
        return queryset.select_related("author", "category").prefetch_related("tags")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            # Add 'post' to context for template compatibility
            context["post"] = self.object

            # Get related posts safely
            try:
                context["related_posts"] = self.object.related_posts[:3]
            except Exception:
                context["related_posts"] = BlogPost.objects.filter(
                    status="published"
                ).exclude(id=self.object.id)[:3]

            # Get comments safely
            try:
                context["comments"] = (
                    self.object.comments.filter(is_approved=True, parent=None)
                    .select_related("author")
                    .prefetch_related("replies")
                )
            except Exception:
                context["comments"] = []

            # Ensure author has all required fields for template
            if self.object.author:
                author = self.object.author
                # Add fallback values for missing fields
                if not hasattr(author, "bio"):
                    author.bio = ""

        except Exception as e:
            # Handle any unexpected errors gracefully
            context["post"] = None
            context["related_posts"] = []
            context["comments"] = []
            # You might want to log this error in production
            print(f"Error in BlogDetailView: {e}")

        return context

    def get_object(self, queryset=None):
        """Override to handle missing objects gracefully"""
        if queryset is None:
            queryset = self.get_queryset()

        slug = self.kwargs.get(self.slug_url_kwarg)
        if not slug:
            raise Http404("No slug provided")

        try:
            obj = queryset.get(slug=slug)
        except BlogPost.DoesNotExist:
            raise Http404("Blog post not found")
        except Exception as e:
            raise Http404(f"Error retrieving blog post: {e}")
        return obj


class ContactView(TemplateView):
    """
    Contact page with form
    """

    template_name = "core/contact.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get main user profile for display (always show super admin profile)
        try:
            from django.contrib.auth import get_user_model

            User = get_user_model()
            superuser = User.objects.get(is_superuser=True)
            context["profile_user"] = superuser
            context["user_profile"] = getattr(superuser, "profile", None)
        except User.DoesNotExist:
            context["profile_user"] = None
            context["user_profile"] = None

        return context


class ChatView(TemplateView):
    """
    Real-time chat page
    """

    template_name = "core/chat.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            # Get user's chat rooms
            context["chat_rooms"] = self.request.user.chat_rooms.filter(is_active=True)
        else:
            context["chat_rooms"] = []

        return context


class ProfileManagementView(TemplateView):
    """
    Profile management page for super admin to upload and edit profile data
    """

    template_name = "core/profile_management.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # For single-user portfolio, always use the super admin
        try:
            superuser = User.objects.get(is_superuser=True)
            profile, created = Profile.objects.get_or_create(user=superuser)
            context["profile"] = profile
            context["created"] = created
            context["user"] = superuser
        except User.DoesNotExist:
            context["profile"] = None
            context["created"] = False
            context["user"] = None

        return context

    def post(self, request, *args, **kwargs):
        # For single-user portfolio, always use the super admin
        try:
            superuser = User.objects.get(is_superuser=True)
            profile, created = Profile.objects.get_or_create(user=superuser)

            # Update user fields
            superuser.first_name = request.POST.get("first_name", superuser.first_name)
            superuser.last_name = request.POST.get("last_name", superuser.last_name)
            superuser.bio = request.POST.get("bio", superuser.bio)
            superuser.location = request.POST.get("location", superuser.location)

            # Handle avatar upload
            if "avatar" in request.FILES:
                superuser.avatar = request.FILES["avatar"]

            superuser.save()

            # Update profile fields
            profile.phone = request.POST.get("phone", profile.phone)
            # Handle experience_years properly
            exp_years = request.POST.get("experience_years", "")
            profile.experience_years = (
                int(exp_years) if exp_years and exp_years.isdigit() else 0
            )
            profile.availability = request.POST.get(
                "availability", profile.availability
            )
            # Handle numeric fields properly - convert empty strings to None
            salary_min = request.POST.get("expected_salary_min", "")
            profile.expected_salary_min = (
                int(salary_min) if salary_min and salary_min.isdigit() else None
            )

            salary_max = request.POST.get("expected_salary_max", "")
            profile.expected_salary_max = (
                int(salary_max) if salary_max and salary_max.isdigit() else None
            )
            profile.preferred_work_type = request.POST.get(
                "preferred_work_type", profile.preferred_work_type
            )

            # Handle resume upload
            if "resume" in request.FILES:
                profile.resume = request.FILES["resume"]

            profile.save()

        except User.DoesNotExist:
            pass

        return redirect("core:profile_management")


# Simple Django Authentication Views
def admin_login(request):
    """Simple Django login view for admin access"""
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)
        if user is not None:
            if user.is_superuser:
                login(request, user)
                messages.success(request, "Successfully logged in!")
                return redirect("core:profile_management")
            else:
                messages.error(request, "Access denied. Admin access required.")
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, "core/login.html")


def admin_logout(request):
    """Simple Django logout view"""
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("core:home")
