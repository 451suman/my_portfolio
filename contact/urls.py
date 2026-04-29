from django.urls import path
from . import views

app_name = 'contact'

urlpatterns = [
    # Contact form
    path('messages/', views.ContactMessageCreateView.as_view(), name='message_create'),
    path('messages/list/', views.ContactMessageListView.as_view(), name='message_list'),
    path('messages/<int:pk>/', views.ContactMessageDetailView.as_view(), name='message_detail'),
    
    # Message status
    path('messages/<int:pk>/read/', views.mark_message_read_view, name='mark_read'),
    path('messages/<int:pk>/responded/', views.mark_message_responded_view, name='mark_responded'),
    
    # Newsletter
    path('newsletter/subscribe/', views.newsletter_subscribe_view, name='newsletter_subscribe'),
    path('newsletter/unsubscribe/', views.newsletter_unsubscribe_view, name='newsletter_unsubscribe'),
    
    # Statistics
    path('stats/', views.contact_stats_view, name='contact_stats'),
]
