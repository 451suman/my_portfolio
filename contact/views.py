from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .models import ContactMessage, EmailTemplate, NewsletterSubscription
from .serializers import (
    ContactMessageSerializer,
    ContactMessageListSerializer,
    EmailTemplateSerializer,
    NewsletterSubscriptionSerializer,
)


class ContactMessageCreateView(generics.CreateAPIView):
    """
    Create contact form messages
    """

    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        contact_message = serializer.save()

        # Send email notification
        try:
            self.send_notification_email(contact_message)
            contact_message.email_sent = True
            contact_message.save()
        except Exception as e:
            # Log error but don't fail the request
            print(f"Email sending failed: {e}")

        return Response(
            {
                "message": "Your message has been sent successfully! We'll get back to you soon.",
                "id": contact_message.id,
            },
            status=status.HTTP_201_CREATED,
        )

    def send_notification_email(self, contact_message):
        """
        Send email notification for new contact message
        """
        subject = f"New Contact Form: {contact_message.subject}"

        # HTML email content
        html_content = render_to_string(
            "contact/email_notification.html", {"contact_message": contact_message}
        )

        # Plain text email content
        text_content = strip_tags(html_content)

        # Send email
        send_mail(
            subject=subject,
            message=text_content,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.EMAIL_HOST_USER],  # Send to admin
            html_message=html_content,
            fail_silently=False,
        )


class ContactMessageListView(generics.ListAPIView):
    """
    List contact messages (admin only)
    """

    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = ["django_filters.rest_framework.DjangoFilterBackend"]
    filterset_fields = ["status", "priority", "inquiry_type"]
    ordering = ["-created_at"]


class ContactMessageDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve and update contact messages (admin only)
    """

    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageListSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def newsletter_subscribe_view(request):
    """
    Subscribe to newsletter
    """
    serializer = NewsletterSubscriptionSerializer(data=request.data)

    if serializer.is_valid():
        email = serializer.validated_data["email"]

        # Check if already subscribed
        if NewsletterSubscription.objects.filter(email=email).exists():
            subscription = NewsletterSubscription.objects.get(email=email)
            if subscription.is_active:
                return Response(
                    {"message": "You are already subscribed to our newsletter."},
                    status=status.HTTP_200_OK,
                )
            else:
                # Reactivate subscription
                subscription.is_active = True
                subscription.save()
                return Response(
                    {
                        "message": "Welcome back! You have been re-subscribed to our newsletter."
                    },
                    status=status.HTTP_200_OK,
                )

        # Create new subscription
        subscription = serializer.save()

        # Send welcome email
        try:
            send_welcome_email(subscription)
        except Exception as e:
            print(f"Welcome email failed: {e}")

        return Response(
            {"message": "Thank you for subscribing to our newsletter!"},
            status=status.HTTP_201_CREATED,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def newsletter_unsubscribe_view(request):
    """
    Unsubscribe from newsletter
    """
    email = request.data.get("email")

    if not email:
        return Response(
            {"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        subscription = NewsletterSubscription.objects.get(email=email)
        subscription.unsubscribe()
        return Response(
            {"message": "You have been successfully unsubscribed from our newsletter."},
            status=status.HTTP_200_OK,
        )
    except NewsletterSubscription.DoesNotExist:
        return Response(
            {"message": "You were not subscribed to our newsletter."},
            status=status.HTTP_200_OK,
        )


def send_welcome_email(subscription):
    """
    Send welcome email for newsletter subscription
    """
    subject = "Welcome to Our Newsletter!"

    html_content = render_to_string(
        "contact/welcome_email.html", {"subscription": subscription}
    )

    text_content = strip_tags(html_content)

    send_mail(
        subject=subject,
        message=text_content,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[subscription.email],
        html_message=html_content,
        fail_silently=False,
    )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def mark_message_read_view(request, message_id):
    """
    Mark contact message as read
    """
    try:
        message = ContactMessage.objects.get(id=message_id)
        message.mark_as_read()
        return Response(
            {"message": "Message marked as read"}, status=status.HTTP_200_OK
        )
    except ContactMessage.DoesNotExist:
        return Response(
            {"error": "Message not found"}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def mark_message_responded_view(request, message_id):
    """
    Mark contact message as responded
    """
    try:
        message = ContactMessage.objects.get(id=message_id)
        message.mark_as_responded()
        return Response(
            {"message": "Message marked as responded"}, status=status.HTTP_200_OK
        )
    except ContactMessage.DoesNotExist:
        return Response(
            {"error": "Message not found"}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def contact_stats_view(request):
    """
    Get contact form statistics
    """
    stats = {
        "total_messages": ContactMessage.objects.count(),
        "unread_messages": ContactMessage.objects.filter(status="unread").count(),
        "read_messages": ContactMessage.objects.filter(status="read").count(),
        "responded_messages": ContactMessage.objects.filter(status="responded").count(),
        "newsletter_subscribers": NewsletterSubscription.objects.filter(
            is_active=True
        ).count(),
        "messages_by_priority": {
            "high": ContactMessage.objects.filter(priority="high").count(),
            "medium": ContactMessage.objects.filter(priority="medium").count(),
            "low": ContactMessage.objects.filter(priority="low").count(),
            "urgent": ContactMessage.objects.filter(priority="urgent").count(),
        },
        "messages_by_type": {
            "general": ContactMessage.objects.filter(inquiry_type="general").count(),
            "collaboration": ContactMessage.objects.filter(
                inquiry_type="collaboration"
            ).count(),
            "job_offer": ContactMessage.objects.filter(
                inquiry_type="job_offer"
            ).count(),
            "project": ContactMessage.objects.filter(inquiry_type="project").count(),
            "feedback": ContactMessage.objects.filter(inquiry_type="feedback").count(),
            "other": ContactMessage.objects.filter(inquiry_type="other").count(),
        },
    }

    return Response(stats)
