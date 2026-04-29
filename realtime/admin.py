from django.contrib import admin
from .models import ChatRoom, ChatMessage, Notification, OnlineUser


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "slug",
        "room_type",
        "is_active",
        "max_participants",
        "participant_count",
        "created_by",
        "last_activity",
    ]
    list_filter = ["room_type", "is_active", "created_at"]
    search_fields = ["name", "slug", "description"]
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ["participants"]
    ordering = ["-last_activity"]

    fieldsets = (
        ("Basic Information", {"fields": ("name", "slug", "room_type", "description")}),
        ("Settings", {"fields": ("is_active", "max_participants", "allow_anonymous")}),
        ("Relations", {"fields": ("created_by", "participants")}),
    )

    def participant_count(self, obj):
        return obj.participants.count()

    participant_count.short_description = "Participants"


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 1
    readonly_fields = ["created_at", "updated_at"]
    fields = [
        "author",
        "content",
        "message_type",
        "is_edited",
        "is_deleted",
        "created_at",
    ]
    ordering = ["-created_at"]


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = [
        "room",
        "author",
        "content_preview",
        "message_type",
        "is_edited",
        "is_deleted",
        "created_at",
    ]
    list_filter = ["message_type", "is_edited", "is_deleted", "created_at"]
    search_fields = ["content", "author__username", "room__name"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        (
            "Message Information",
            {"fields": ("room", "author", "content", "message_type")},
        ),
        ("Media", {"fields": ("file", "image")}),
        ("Relations", {"fields": ("reply_to",)}),
        ("Status", {"fields": ("is_edited", "edited_at", "is_deleted", "deleted_at")}),
        ("Reactions", {"fields": ("reactions",)}),
    )

    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

    content_preview.short_description = "Content"


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        "recipient",
        "sender",
        "notification_type",
        "title",
        "is_read",
        "created_at",
    ]
    list_filter = ["notification_type", "is_read", "created_at"]
    search_fields = ["title", "message", "recipient__username", "sender__username"]
    ordering = ["-created_at"]

    fieldsets = (
        (
            "Notification Information",
            {
                "fields": (
                    "recipient",
                    "sender",
                    "notification_type",
                    "title",
                    "message",
                )
            },
        ),
        ("Related Object", {"fields": ("content_type", "object_id")}),
        ("Status", {"fields": ("is_read", "read_at")}),
        ("Additional Data", {"fields": ("data",)}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("recipient", "sender")


@admin.register(OnlineUser)
class OnlineUserAdmin(admin.ModelAdmin):
    list_display = ["user", "channel_name", "is_online", "last_seen"]
    list_filter = ["is_online", "last_seen"]
    search_fields = ["user__username", "channel_name"]
    ordering = ["-last_seen"]
    readonly_fields = ["channel_name", "last_seen"]

    fieldsets = (
        ("User Information", {"fields": ("user", "channel_name")}),
        ("Status", {"fields": ("is_online", "last_seen")}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")

    actions = ["mark_offline"]

    def mark_offline(self, request, queryset):
        queryset.update(is_online=False)

    mark_offline.short_description = "Mark selected users as offline"
