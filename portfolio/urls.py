from django.urls import path
from . import views

app_name = 'portfolio'

urlpatterns = [
    # Projects
    path('projects/', views.ProjectListView.as_view(), name='project_list'),
    path('projects/featured/', views.FeaturedProjectsView.as_view(), name='featured_projects'),
    path('projects/<slug:slug>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('projects/<slug:slug>/toggle-featured/', views.toggle_project_featured_view, name='toggle_featured'),
    path('users/<str:username>/projects/', views.UserProjectsView.as_view(), name='user_projects'),
    
    # Categories
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    
    # Skills
    path('skills/', views.SkillListView.as_view(), name='skill_list'),
    path('skills/<slug:slug>/', views.SkillDetailView.as_view(), name='skill_detail'),
    path('skills/by-category/', views.skills_by_category_view, name='skills_by_category'),
    
    # Experience
    path('experience/', views.ExperienceListView.as_view(), name='experience_list'),
    path('experience/<int:pk>/', views.ExperienceDetailView.as_view(), name='experience_detail'),
    
    # Stats
    path('stats/', views.portfolio_stats_view, name='portfolio_stats'),
    path('stats/<str:username>/', views.portfolio_stats_view, name='user_portfolio_stats'),
]
