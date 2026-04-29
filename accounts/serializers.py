from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, Profile


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    """
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        min_length=8
    )
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'password', 'password_confirm', 'bio', 'github_username',
            'linkedin_url', 'twitter_url', 'website_url', 'location'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        # Create profile for the user
        Profile.objects.create(user=user)
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include email and password')


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile information
    """
    full_name = serializers.ReadOnlyField()
    github_profile_url = serializers.ReadOnlyField()
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'bio', 'avatar', 'avatar_url', 'github_username',
            'github_profile_url', 'linkedin_url', 'twitter_url', 'website_url',
            'location', 'is_developer', 'date_joined'
        ]
        read_only_fields = ['id', 'email', 'date_joined']

    def get_avatar_url(self, obj):
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None


class ProfileDetailSerializer(serializers.ModelSerializer):
    """
    Detailed profile serializer including extended profile information
    """
    user = UserProfileSerializer(read_only=True)
    skills = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            'user', 'resume', 'phone', 'experience_years', 'availability',
            'expected_salary_min', 'expected_salary_max', 'preferred_work_type',
            'skills', 'created_at', 'updated_at'
        ]

    def get_skills(self, obj):
        """Get user's skills from portfolio projects"""
        from portfolio.models import Skill
        # Get skills from user's projects
        projects_skills = Skill.objects.filter(
            projects__owner=obj.user
        ).distinct()
        return SkillSerializer(projects_skills, many=True).data


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile
    """
    class Meta:
        model = Profile
        fields = [
            'resume', 'phone', 'experience_years', 'availability',
            'expected_salary_min', 'expected_salary_max', 'preferred_work_type'
        ]

    def validate(self, attrs):
        if attrs.get('expected_salary_min') and attrs.get('expected_salary_max'):
            if attrs['expected_salary_min'] > attrs['expected_salary_max']:
                raise serializers.ValidationError(
                    "Minimum salary cannot be greater than maximum salary"
                )
        return attrs


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user information
    """
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'bio', 'avatar', 'github_username',
            'linkedin_url', 'twitter_url', 'website_url', 'location'
        ]

    def validate_avatar(self, value):
        """Validate avatar file size and type"""
        if value:
            # Check file size (max 5MB)
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError("Avatar file size cannot exceed 5MB")
            
            # Check file type
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if value.content_type not in allowed_types:
                raise serializers.ValidationError(
                    "Avatar must be a valid image file (JPEG, PNG, GIF, or WebP)"
                )
        return value


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for password change
    """
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        min_length=8
    )
    new_password_confirm = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect")
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


# Import this at the end to avoid circular imports
from portfolio.serializers import SkillSerializer
