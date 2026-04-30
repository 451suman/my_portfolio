from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Includes additional fields for portfolio functionality.
    """

    email = models.EmailField(unique=True)
    is_developer = models.BooleanField(default=True)
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    location = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "auth_user"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.username

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class Profile(models.Model):
    """
    Extended profile model for additional user information.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    resume = models.FileField(upload_to="resumes/", blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    availability = models.CharField(
        max_length=20,
        choices=[
            ("available", "Available"),
            ("busy", "Busy"),
            ("open_to_offers", "Open to Offers"),
        ],
        default="available",
    )
    expected_salary_min = models.PositiveIntegerField(blank=True, null=True)
    expected_salary_max = models.PositiveIntegerField(blank=True, null=True)
    preferred_work_type = models.CharField(
        max_length=20,
        choices=[
            ("remote", "Remote"),
            ("onsite", "On-site"),
            ("hybrid", "Hybrid"),
        ],
        default="remote",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    def __str__(self):
        return f"{self.user.username}'s Profile"
