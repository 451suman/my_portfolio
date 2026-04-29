from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("projects/", views.ProjectsView.as_view(), name="projects"),
    path(
        "projects/<slug:slug>/",
        views.ProjectDetailView.as_view(),
        name="project_detail",
    ),
    path("blog/", views.BlogView.as_view(), name="blog"),
    path("blog/<slug:slug>/", views.BlogDetailView.as_view(), name="blog_detail"),
    path("contact/", views.ContactView.as_view(), name="contact"),
    path("chat/", views.ChatView.as_view(), name="chat"),
    path("profile/", views.ProfileManagementView.as_view(), name="profile_management"),
    path("login/", views.admin_login, name="admin_login"),
    path("logout/", views.admin_logout, name="admin_logout"),
]
