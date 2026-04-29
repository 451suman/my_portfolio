from django.db import models
from django.conf import settings
from django.utils import timezone


class ChatRoom(models.Model):
    """
    Chat rooms for real-time communication
    """

    ROOM_TYPES = [
        ("public", "Public"),
        ("private", "Private"),
        ("direct", "Direct Message"),
        ("project", "Project-based"),
    ]

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default="public")

    # Room settings
    is_active = models.BooleanField(default=True)
    max_participants = models.PositiveIntegerField(null=True, blank=True)
    allow_anonymous = models.BooleanField(default=False)

    # Relationships
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_rooms"
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="chat_rooms", blank=True
    )

    # Metadata
    last_activity = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-last_activity"]
        indexes = [
            models.Index(fields=["room_type", "is_active"]),
            models.Index(fields=["last_activity"]),
        ]

    def __str__(self):
        return self.name

    def join_room(self, user):
        """Add user to room participants"""
        if user not in self.participants.all():
            self.participants.add(user)
            self.last_activity = timezone.now()
            self.save(update_fields=["last_activity"])

    def leave_room(self, user):
        """Remove user from room participants"""
        if user in self.participants.all():
            self.participants.remove(user)
            self.last_activity = timezone.now()
            self.save(update_fields=["last_activity"])

    @property
    def participant_count(self):
        return self.participants.count()

    @property
    def latest_message(self):
        return self.messages.order_by("-created_at").first()


class ChatMessage(models.Model):
    """
    Chat messages in rooms
    """

    MESSAGE_TYPES = [
        ("text", "Text"),
        ("image", "Image"),
        ("file", "File"),
        ("system", "System"),
    ]

    room = models.ForeignKey(
        ChatRoom, on_delete=models.CASCADE, related_name="messages"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chat_messages"
    )
    content = models.TextField()
    message_type = models.CharField(
        max_length=20, choices=MESSAGE_TYPES, default="text"
    )

    # File attachments
    file = models.FileField(upload_to="chat/files/", blank=True, null=True)
    image = models.ImageField(upload_to="chat/images/", blank=True, null=True)

    # Message metadata
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # Reply functionality
    reply_to = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )

    # Reactions
    reactions = models.JSONField(default=dict, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["room", "created_at"]),
            models.Index(fields=["author"]),
        ]

    def __str__(self):
        return f"{self.author.username} in {self.room.name}: {self.content[:50]}"

    def edit_message(self, new_content):
        """Edit message content"""
        self.content = new_content
        self.is_edited = True
        self.edited_at = timezone.now()
        self.save(update_fields=["content", "is_edited", "edited_at"])

    def soft_delete(self):
        """Soft delete message"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])

    def add_reaction(self, user, emoji):
        """Add or remove reaction"""
        user_id = str(user.id)
        if user_id not in self.reactions:
            self.reactions[user_id] = []

        if emoji in self.reactions[user_id]:
            self.reactions[user_id].remove(emoji)
        else:
            self.reactions[user_id].append(emoji)

        # Clean up empty reactions
        if not self.reactions[user_id]:
            del self.reactions[user_id]

        self.save(update_fields=["reactions"])


class Notification(models.Model):
    """
    Real-time notifications for users
    """

    NOTIFICATION_TYPES = [
        ("message", "New Message"),
        ("project_like", "Project Like"),
        ("blog_comment", "Blog Comment"),
        ("contact_form", "Contact Form"),
        ("system", "System Notification"),
        ("mention", "Mention"),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_notifications",
        null=True,
        blank=True,
    )

    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()

    # Link to related object
    content_type = models.ForeignKey(
        "contenttypes.ContentType", on_delete=models.CASCADE, null=True, blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)

    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    data = models.JSONField(default=dict, blank=True)  # Additional data

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "is_read"]),
            models.Index(fields=["notification_type"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.title} for {self.recipient.username}"

    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=["is_read", "read_at"])


class OnlineUser(models.Model):
    """
    Track online users for real-time features
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="online_status"
    )
    channel_name = models.CharField(max_length=255, unique=True)
    last_seen = models.DateTimeField(auto_now=True)
    is_online = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=["is_online", "last_seen"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {'Online' if self.is_online else 'Offline'}"

    @classmethod
    def mark_online(cls, user, channel_name):
        """Mark user as online"""
        online_user, created = cls.objects.update_or_create(
            user=user,
            defaults={
                "channel_name": channel_name,
                "is_online": True,
                "last_seen": timezone.now(),
            },
        )
        return online_user

    @classmethod
    def mark_offline(cls, user):
        """Mark user as offline"""
        cls.objects.filter(user=user).update(is_online=False)

    @classmethod
    def get_online_users(cls):
        """Get all currently online users"""
        return cls.objects.filter(is_online=True).select_related("user")
