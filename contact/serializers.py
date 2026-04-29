from rest_framework import serializers
from .models import ContactMessage, EmailTemplate, NewsletterSubscription


class ContactMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for contact form messages
    """
    class Meta:
        model = ContactMessage
        fields = [
            'id', 'name', 'email', 'phone', 'company', 'website',
            'subject', 'message', 'inquiry_type', 'priority'
        ]

    def create(self, validated_data):
        # Add metadata from request
        request = self.context.get('request')
        if request:
            validated_data['ip_address'] = self.get_client_ip(request)
            validated_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
            validated_data['referrer'] = request.META.get('HTTP_REFERER', '')
        
        return super().create(validated_data)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class EmailTemplateSerializer(serializers.ModelSerializer):
    """
    Serializer for email templates
    """
    class Meta:
        model = EmailTemplate
        fields = [
            'id', 'name', 'subject', 'html_content', 'text_content',
            'is_active', 'created_at', 'updated_at'
        ]


class NewsletterSubscriptionSerializer(serializers.ModelSerializer):
    """
    Serializer for newsletter subscriptions
    """
    class Meta:
        model = NewsletterSubscription
        fields = ['id', 'email', 'name', 'is_active', 'subscribed_at']

    def create(self, validated_data):
        # Add IP address from request
        request = self.context.get('request')
        if request:
            validated_data['ip_address'] = self.get_client_ip(request)
        
        return super().create(validated_data)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class ContactMessageListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing contact messages (admin view)
    """
    author_name = serializers.CharField(source='name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    inquiry_type_display = serializers.CharField(source='get_inquiry_type_display', read_only=True)

    class Meta:
        model = ContactMessage
        fields = [
            'id', 'name', 'email', 'subject', 'status', 'status_display',
            'priority', 'priority_display', 'inquiry_type', 'inquiry_type_display',
            'assigned_to', 'email_sent', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
