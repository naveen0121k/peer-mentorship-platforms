from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.http import JsonResponse

from .models import Profile, MentorshipRequest, Message, MentorshipSession, Notification
from .forms import ProfileForm, MentorshipRequestForm, MessageForm, MentorshipSessionForm

User = get_user_model()

# Mentor/Mentee Dashboard
@login_required
def dashboard_view(request):
    if request.user.is_staff:
        pending_requests = MentorshipRequest.objects.filter(mentor=request.user, status="pending")
        mentoring_sessions = MentorshipSession.objects.filter(mentor=request.user).order_by('scheduled_time')
        upcoming_sessions = mentoring_sessions
    else:
        pending_requests = None
        upcoming_sessions = MentorshipSession.objects.filter(mentee=request.user).order_by('scheduled_time')
        mentoring_sessions = None

    unseen_notifications = Notification.objects.filter(user=request.user, is_read=False)

    return render(request, 'dashboard/dashboard.html', {
        'pending_requests': pending_requests,
        'upcoming_sessions': upcoming_sessions,
        'mentoring_sessions': mentoring_sessions,
        'unseen_notifications': unseen_notifications,
    })

# Profile View
@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    form = ProfileForm(request.POST or None, request.FILES or None, instance=profile)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Your profile has been updated.")
        return redirect('dashboard')

    return render(request, 'dashboard/profile.html', {'form': form})

# Send Request
@login_required
def send_request_view(request):
    if request.method == "POST":
        form = MentorshipRequestForm(request.POST)
        if form.is_valid():
            mentorship_request = form.save(commit=False)
            mentorship_request.mentee = request.user
            mentorship_request.save()
            send_notification(mentorship_request.mentor, f"You have a new mentorship request from {request.user.username}.")
            messages.success(request, "Your mentorship request has been sent!")
            return redirect('dashboard')
    else:
        form = MentorshipRequestForm()
        form.fields['mentor'].queryset = User.objects.filter(is_staff=True).exclude(id=request.user.id)

    return render(request, 'dashboard/mentorship_request.html', {'form': form})

# Accept Request
@login_required
def accept_request_view(request, request_id):
    mentorship_request = get_object_or_404(MentorshipRequest, id=request_id, mentor=request.user)
    if mentorship_request.status == "pending":
        mentorship_request.status = "accepted"
        mentorship_request.save()
        send_notification(mentorship_request.mentee, f"Your mentorship request to {mentorship_request.mentor.username} has been accepted! 🎉")
        messages.success(request, "You have accepted the mentorship request.")
    return redirect('dashboard')

# Decline Request
@login_required
def decline_request_view(request, request_id):
    mentorship_request = get_object_or_404(MentorshipRequest, id=request_id, mentor=request.user)
    if mentorship_request.status == "pending":
        mentorship_request.status = "declined"
        mentorship_request.save()
        send_notification(mentorship_request.mentee, f"Your mentorship request to {mentorship_request.mentor.username} has been declined.")
        messages.warning(request, "You have declined the mentorship request.")
    return redirect('dashboard')

# Chat View
@login_required
def chat_view(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    messages_qs = Message.objects.filter(
        sender__in=[request.user, other_user],
        receiver__in=[request.user, other_user]
    ).order_by('timestamp')

    form = MessageForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        message = form.save(commit=False)
        message.sender = request.user
        message.receiver = other_user
        message.save()
        send_notification(other_user, f"You have a new message from {request.user.username}.")
        return redirect('chat', user_id=other_user.id)

    return render(request, 'dashboard/chat.html', {'messages': messages_qs, 'form': form, 'other_user': other_user})

# Schedule Session View
@login_required
def schedule_session_view(request, request_id):
    mentorship_request = get_object_or_404(MentorshipRequest, id=request_id, mentor=request.user, status='accepted')
    form = MentorshipSessionForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        session = form.save(commit=False)
        session.mentorship_request = mentorship_request
        session.mentor = request.user
        session.mentee = mentorship_request.mentee
        session.save()
        send_notification(session.mentee, f"Your session with {request.user.username} is scheduled for {session.scheduled_time}.")
        messages.success(request, "Mentorship session scheduled successfully!")
        return redirect('dashboard')

    return render(request, 'dashboard/schedule_session.html', {
        'form': form,
        'mentorship_request': mentorship_request,
    })

# Notifications List
@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'dashboard/notifications.html', {'notifications': notifications})

# Unread Notifications Count (JSON)
@login_required
def unread_notifications_count(request):
    unread_count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({'unread_count': unread_count})

# Helper: Send Notification
def send_notification(user, message):
    Notification.objects.create(user=user, message=message)
