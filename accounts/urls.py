from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication endpoints
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.CustomTokenObtainPairView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Profile endpoints
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/detail/', views.ProfileDetailView.as_view(), name='profile_detail'),
    path('password/change/', views.PasswordChangeView.as_view(), name='password_change'),
    
    # User management
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('stats/', views.user_stats_view, name='user_stats'),
    path('online-users/', views.online_users_view, name='online_users'),
]
