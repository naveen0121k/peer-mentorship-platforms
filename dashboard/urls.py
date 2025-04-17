from django.urls import path
from .views import (
    dashboard_view,
    profile_view,
    send_request_view,
    accept_request_view,
    decline_request_view,
    chat_view,
    schedule_session_view,
    notifications_view,
    unread_notifications_count
)

urlpatterns = [
    path('', dashboard_view, name='dashboard'),  # Dashboard for both mentor and mentee
    path('profile/', profile_view, name='profile'),  # Profile view to update user profile
    path('request/', send_request_view, name='send_request'),  # Send mentorship request
    path('request/accept/<int:request_id>/', accept_request_view, name='accept_request'),  # Accept mentorship request
    path('request/decline/<int:request_id>/', decline_request_view, name='decline_request'),  # Decline mentorship request
    path('chat/<int:user_id>/', chat_view, name='chat'),  # Chat with another user
    path('request/schedule/<int:request_id>/', schedule_session_view, name='schedule_session'),  # Schedule a mentorship session
    path('notifications/', notifications_view, name='notifications'),  # View all notifications
    path('notifications/unread_count/', unread_notifications_count, name='unread_notifications_count'),  # Get count of unread notifications
]
