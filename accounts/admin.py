from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        "username",
        "email",
        "first_name",
        "last_name",
        "is_developer",
        "is_staff",
        "date_joined",
    ]
    list_filter = ["is_developer", "is_staff", "is_superuser", "date_joined"]
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering = ["-date_joined"]

    fieldsets = (
        (None, {"fields": ("username", "email", "password")}),
        (
            "Personal info",
            {"fields": ("first_name", "last_name", "bio", "avatar", "location")},
        ),
        (
            "Professional",
            {"fields": ("is_developer",)},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2"),
            },
        ),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "phone",
        "experience_years",
        "availability",
        "preferred_work_type",
        "created_at",
    ]
    list_filter = ["availability", "preferred_work_type", "created_at"]
    search_fields = ["user__username", "user__email", "phone"]
    ordering = ["-created_at"]

    fieldsets = (
        ("User", {"fields": ("user",)}),
        ("Contact", {"fields": ("phone", "resume")}),
        (
            "Professional",
            {
                "fields": (
                    "experience_years",
                    "availability",
                    "expected_salary_min",
                    "expected_salary_max",
                    "preferred_work_type",
                )
            },
        ),
        ("Metadata", {"fields": ("created_at", "updated_at")}),
    )

    readonly_fields = ["created_at", "updated_at"]
