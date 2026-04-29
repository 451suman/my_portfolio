from django.contrib import admin
from .models import ContactMessage, EmailTemplate, NewsletterSubscription


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "email",
        "subject",
        "inquiry_type",
        "priority",
        "status",
        "email_sent",
        "created_at",
    ]
    list_filter = ["status", "priority", "inquiry_type", "email_sent", "created_at"]
    search_fields = ["name", "email", "subject", "message"]
    ordering = ["-created_at"]
    readonly_fields = ["ip_address", "user_agent", "referrer", "created_at"]

    fieldsets = (
        (
            "Contact Information",
            {"fields": ("name", "email", "phone", "company", "website")},
        ),
        (
            "Message Details",
            {"fields": ("subject", "message", "inquiry_type", "priority")},
        ),
        (
            "Status",
            {
                "fields": (
                    "status",
                    "assigned_to",
                    "email_sent",
                    "email_sent_at",
                    "responded_at",
                )
            },
        ),
        (
            "Metadata",
            {
                "fields": (
                    "ip_address",
                    "user_agent",
                    "referrer",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    actions = ["mark_as_read", "mark_as_responded"]

    def mark_as_read(self, request, queryset):
        queryset.update(status="read")

    mark_as_read.short_description = "Mark selected messages as read"

    def mark_as_responded(self, request, queryset):
        queryset.update(status="responded")

    mark_as_responded.short_description = "Mark selected messages as responded"


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "subject", "is_active", "created_at", "updated_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "subject"]
    ordering = ["name"]

    fieldsets = (
        ("Basic Information", {"fields": ("name", "subject", "is_active")}),
        ("Content", {"fields": ("html_content", "text_content")}),
    )


@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ["email", "name", "is_active", "subscribed_at", "unsubscribed_at"]
    list_filter = ["is_active", "subscribed_at", "unsubscribed_at"]
    search_fields = ["email", "name"]
    ordering = ["-subscribed_at"]
    readonly_fields = ["subscribed_at", "ip_address"]

    fieldsets = (
        ("Subscription Information", {"fields": ("email", "name", "is_active")}),
        ("Metadata", {"fields": ("subscribed_at", "unsubscribed_at", "ip_address")}),
    )

    actions = ["unsubscribe_selected", "resubscribe_selected"]

    def unsubscribe_selected(self, request, queryset):
        for subscription in queryset:
            subscription.unsubscribe()

    unsubscribe_selected.short_description = "Unsubscribe selected users"

    def resubscribe_selected(self, request, queryset):
        queryset.update(is_active=True, unsubscribed_at=None)

    resubscribe_selected.short_description = "Resubscribe selected users"
