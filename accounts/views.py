from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator

from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    ProfileDetailSerializer,
    ProfileUpdateSerializer,
    UserUpdateSerializer,
    PasswordChangeSerializer,
)
from .models import Profile

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token view that uses email instead of username
    """

    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": UserProfileSerializer(user, context={"request": request}).data,
            }
        )


class RegisterView(generics.CreateAPIView):
    """
    User registration endpoint
    """

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate tokens for new user
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": UserProfileSerializer(user, context={"request": request}).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            },
            status=status.HTTP_201_CREATED,
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Get and update user profile
    """

    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ProfileDetailView(generics.RetrieveUpdateAPIView):
    """
    Get and update detailed profile information
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile

    def get_serializer_class(self):
        if self.request.method == "PUT" or self.request.method == "PATCH":
            return ProfileUpdateSerializer
        return ProfileDetailSerializer


class PasswordChangeView(generics.GenericAPIView):
    """
    Change user password
    """

    serializer_class = PasswordChangeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "Password changed successfully"}, status=status.HTTP_200_OK
        )


class UserListView(generics.ListAPIView):
    """
    List all users (for admin purposes)
    """

    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ["username", "first_name", "last_name", "email"]
    ordering_fields = ["date_joined", "username"]
    ordering = ["-date_joined"]


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def logout_view(request):
    """
    Logout user by blacklisting refresh token
    """
    try:
        refresh_token = request.data.get("refresh_token")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()

        return Response(
            {"message": "Successfully logged out"}, status=status.HTTP_200_OK
        )

    except Exception as e:
        return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def user_stats_view(request):
    """
    Get user statistics for dashboard
    """
    user = request.user

    # Get counts from related models
    stats = {
        "projects_count": user.projects.count(),
        "blog_posts_count": user.blog_posts.count(),
        "experiences_count": user.experiences.count(),
        "unread_notifications_count": user.notifications.filter(is_read=False).count(),
        "profile_completion": calculate_profile_completion(user),
    }

    return Response(stats)


def calculate_profile_completion(user):
    """
    Calculate profile completion percentage
    """
    profile_fields = [
        user.first_name,
        user.last_name,
        user.bio,
        user.avatar,
        user.github_username,
        user.linkedin_url,
        user.location,
    ]

    profile = getattr(user, "profile", None)
    if profile:
        profile_fields.extend([profile.phone, profile.resume, profile.experience_years])

    filled_fields = sum(1 for field in profile_fields if field)
    total_fields = len(profile_fields)

    return round((filled_fields / total_fields) * 100, 0) if total_fields > 0 else 0


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def online_users_view(request):
    """
    Get list of online users
    """
    from realtime.models import OnlineUser

    online_users = OnlineUser.get_online_users()
    users_data = []

    for online_user in online_users:
        user_data = UserProfileSerializer(
            online_user.user, context={"request": request}
        ).data
        user_data["last_seen"] = online_user.last_seen
        users_data.append(user_data)

    return Response(users_data)
