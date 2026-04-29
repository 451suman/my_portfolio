from django.db import models
from django.conf import settings
from django.urls import reverse


class Category(models.Model):
    """
    Project categories for organization
    """

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Skill(models.Model):
    """
    Technical skills and technologies
    """

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    category = models.CharField(
        max_length=50,
        choices=[
            ("frontend", "Frontend"),
            ("backend", "Backend"),
            ("database", "Database"),
            ("devops", "DevOps"),
            ("mobile", "Mobile"),
            ("other", "Other"),
        ],
        default="backend",
    )
    proficiency_level = models.PositiveIntegerField(
        choices=[(i, f"{i}%") for i in range(0, 101, 10)], default=50
    )
    icon = models.CharField(
        max_length=50, blank=True, help_text="Font Awesome icon class"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Project(models.Model):
    """
    Portfolio projects with comprehensive details
    """

    STATUS_CHOICES = [
        ("completed", "Completed"),
        ("in_progress", "In Progress"),
        ("planned", "Planned"),
        ("on_hold", "On Hold"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    short_description = models.CharField(
        max_length=200, help_text="Brief description for cards"
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="completed"
    )
    featured = models.BooleanField(default=False, help_text="Show in featured projects")
    priority = models.PositiveIntegerField(
        default=100,
        help_text="Priority for ordering (1 = highest priority, higher numbers = lower priority). Duplicates allowed.",
    )

    # Technical details
    architecture_explanation = models.TextField(
        help_text="Explain the architecture, design patterns, and technical decisions"
    )
    challenges_solved = models.TextField(
        blank=True, help_text="Describe main challenges and how you solved them"
    )

    # Links
    github_url = models.URLField(blank=True)
    live_demo_url = models.URLField(blank=True)
    project_url = models.URLField(blank=True, help_text="Main project website")
    show_code_button = models.BooleanField(
        default=True,
        help_text="Show 'View Code' button that links to GitHub repository",
    )

    # Media
    cover_image = models.ImageField(upload_to="projects/covers/", blank=True, null=True)

    # Relationships
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="projects"
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True
    )
    skills = models.ManyToManyField(Skill, related_name="projects", blank=True)

    # Metadata
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    team_size = models.PositiveIntegerField(
        default=1, help_text="Number of team members"
    )
    is_personal_project = models.BooleanField(default=True)
    is_open_source = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["priority", "-featured", "-created_at"]
        indexes = [
            models.Index(fields=["priority", "featured", "status"]),
            models.Index(fields=["owner"]),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("portfolio:project_detail", kwargs={"slug": self.slug})

    @property
    def duration_months(self):
        if self.start_date and self.end_date:
            return (
                (self.end_date.year - self.start_date.year) * 12
                + (self.end_date.month - self.start_date.month)
                + 1
            )
        return None

    @property
    def main_tech_stack(self):
        """Return top 3 skills for display"""
        return self.skills.all()[:3]


class ProjectImage(models.Model):
    """
    Multiple images for a project
    """

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="projects/gallery/")
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.project.title} - Image {self.order}"


class Experience(models.Model):
    """
    Professional experience entries
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="experiences"
    )
    company = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(
        blank=True, null=True, help_text="Leave blank if current"
    )
    is_current_job = models.BooleanField(default=False)
    company_logo = models.ImageField(
        upload_to="experience/logos/", blank=True, null=True
    )
    company_website = models.URLField(blank=True)
    skills_used = models.ManyToManyField(Skill, related_name="experiences", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_current_job", "-start_date"]

    def __str__(self):
        return f"{self.position} at {self.company}"


class SocialLink(models.Model):
    """
    Social media links for portfolio
    """

    PLATFORM_CHOICES = [
        ("github", "GitHub"),
        ("linkedin", "LinkedIn"),
        ("twitter", "Twitter"),
        ("email", "Email"),
        ("instagram", "Instagram"),
        ("facebook", "Facebook"),
        ("youtube", "YouTube"),
        ("website", "Website"),
    ]

    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, unique=True)
    url = models.URLField(max_length=255, help_text="URL to the social media profile")
    icon_class = models.CharField(max_length=50, help_text="Font Awesome icon class")
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(
        default=0, help_text="Order in which to display"
    )

    class Meta:
        ordering = ["display_order", "platform"]
        verbose_name = "Social Link"
        verbose_name_plural = "Social Links"

    def __str__(self):
        return f"{self.get_platform_display()}: {self.url}"
