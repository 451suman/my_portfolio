from django.contrib import admin
from .models import Category, Skill, Project, ProjectImage, Experience, SocialLink


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "description", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["name", "description"]
    prepopulated_fields = {"slug": ("name",)}
    ordering = ["name"]


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "slug",
        "category",
        "proficiency_level",
        "icon",
        "created_at",
    ]
    list_filter = ["category", "proficiency_level", "created_at"]
    search_fields = ["name", "category"]
    prepopulated_fields = {"slug": ("name",)}
    ordering = ["name"]


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    ordering = ["order"]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "slug",
        "owner",
        "priority",
        "status",
        "featured",
        "category",
        "created_at",
    ]
    list_filter = ["status", "featured", "category", "created_at"]
    search_fields = ["title", "description", "short_description"]
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ["skills"]
    inlines = [ProjectImageInline]
    ordering = ["-created_at"]
    list_editable = ["priority", "featured"]

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("title", "slug", "owner", "priority", "status", "featured")},
        ),
        (
            "Content",
            {
                "fields": (
                    "description",
                    "short_description",
                    "architecture_explanation",
                    "challenges_solved",
                )
            },
        ),
        (
            "Links",
            {
                "fields": (
                    "github_url",
                    "show_code_button",
                    "live_demo_url",
                    "project_url",
                    "cover_image",
                )
            },
        ),
        ("Classification", {"fields": ("category", "skills")}),
        (
            "Metadata",
            {
                "fields": (
                    "start_date",
                    "end_date",
                    "team_size",
                    "is_personal_project",
                    "is_open_source",
                )
            },
        ),
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("owner", "category")
            .prefetch_related("skills")
        )

    def save_model(self, request, obj, form, change):
        # Ensure priority is a positive integer
        if obj.priority is None or obj.priority < 1:
            obj.priority = 100  # Default priority
        super().save_model(request, obj, form, change)


@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    list_display = ["project", "caption", "order", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["project__title", "caption"]
    ordering = ["project", "order"]


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "company",
        "position",
        "start_date",
        "end_date",
        "is_current_job",
        "created_at",
    ]
    list_filter = ["is_current_job", "start_date", "created_at"]
    search_fields = ["company", "position", "description"]
    filter_horizontal = ["skills_used"]
    ordering = ["-start_date"]

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("user", "company", "position", "is_current_job")},
        ),
        ("Content", {"fields": ("description", "start_date", "end_date")}),
        ("Media", {"fields": ("company_logo", "company_website")}),
        ("Skills", {"fields": ("skills_used",)}),
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("user")
            .prefetch_related("skills_used")
        )


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = [
        "platform",
        "url",
        "icon_class",
        "is_active",
        "display_order",
    ]
    list_filter = ["platform", "is_active"]
    search_fields = ["platform", "url"]
    list_editable = ["is_active", "display_order"]
    ordering = ["display_order", "platform"]

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("platform", "url", "icon_class")},
        ),
        (
            "Display Settings",
            {"fields": ("is_active", "display_order")},
        ),
    )
