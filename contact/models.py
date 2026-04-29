from django.db import models
from django.conf import settings


class ContactMessage(models.Model):
    """
    Contact form messages from visitors
    """

    STATUS_CHOICES = [
        ("unread", "Unread"),
        ("read", "Read"),
        ("responded", "Responded"),
        ("archived", "Archived"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("urgent", "Urgent"),
    ]

    # Contact information
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)

    # Message details
    subject = models.CharField(max_length=200)
    message = models.TextField()

    # Categorization
    inquiry_type = models.CharField(
        max_length=50,
        choices=[
            ("general", "General Inquiry"),
            ("collaboration", "Collaboration"),
            ("job_offer", "Job Offer"),
            ("project", "Project Discussion"),
            ("feedback", "Feedback"),
            ("other", "Other"),
        ],
        default="general",
    )
    priority = models.CharField(
        max_length=20, choices=PRIORITY_CHOICES, default="medium"
    )

    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="unread")
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_messages",
    )

    # Email tracking
    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "priority"]),
            models.Index(fields=["inquiry_type"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.name} - {self.subject}"

    def mark_as_read(self):
        self.status = "read"
        self.save(update_fields=["status"])

    def mark_as_responded(self):
        self.status = "responded"
        from django.utils import timezone

        self.responded_at = timezone.now()
        self.save(update_fields=["status", "responded_at"])


class EmailTemplate(models.Model):
    """
    Email templates for automated responses
    """

    name = models.CharField(max_length=100, unique=True)
    subject = models.CharField(max_length=200)
    html_content = models.TextField()
    text_content = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class NewsletterSubscription(models.Model):
    """
    Newsletter subscription management
    """

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ["-subscribed_at"]

    def __str__(self):
        return f"{self.email} ({'Active' if self.is_active else 'Inactive'})"

    def unsubscribe(self):
        self.is_active = False
        from django.utils import timezone

        self.unsubscribed_at = timezone.now()
        self.save(update_fields=["is_active", "unsubscribed_at"])
