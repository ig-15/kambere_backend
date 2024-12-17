from django.urls import path
from .views import (SignupView, LoginView , ProfileView, FamilyMembersView, UpdateFamilyMemberView, TaskListCreateView , 
    TaskUpdateDeleteView, AdminSignupView, AdminLoginView, ChallengeListCreateView, ChallengeDetailView, ChallengeListCreateView,
    ChallengeDetailView,
    AddQuestionToChallengeView, AnalyticsView,
    SubmitChallengeView, StoryListCreateView, StoryDetailView,
    FamilyChallengeListCreateView, FamilyChallengeDetailView, ChallengeAnswerListCreateView, 
    FamilyStoryDetailView, FamilyStoryListCreateView)


urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('family-members/', FamilyMembersView.as_view(), name='family-members'),
    path('family-members/<int:pk>/', UpdateFamilyMemberView.as_view(), name='update-family-member'),
    path('tasks/', TaskListCreateView.as_view(), name='tasks'),
    path('tasks/<int:pk>/', TaskUpdateDeleteView.as_view(), name='task-detail'),
    path('admin-signup/', AdminSignupView.as_view(), name='admin-signup'),
    path('admin-login/', AdminLoginView.as_view(), name='admin-login'),
    path('challenges/', ChallengeListCreateView.as_view(), name='challenge-list-create'),
    path('challenges/<int:pk>/', ChallengeDetailView.as_view(), name='challenge-detail'),
    path('challenges/<int:challenge_id>/questions/', AddQuestionToChallengeView.as_view(), name='add-question'),
    path('challenges/<int:challenge_id>/submit/', SubmitChallengeView.as_view(), name='submit-challenge'),
    path('stories/', StoryListCreateView.as_view(), name='story-list-create'),
    path('stories/<int:pk>/', StoryDetailView.as_view(), name='story-detail'),
    path('analytics/', AnalyticsView.as_view(), name='analytics'),
    # path('family-challenges/', FamilyChallengeListCreateView.as_view(), name='family-challenge-list-create'),
    # path('family-challenges/<int:pk>/', FamilyChallengeDetailView.as_view(), name='family-challenge-detail'),
    path('challenge-answers/', ChallengeAnswerListCreateView.as_view(), name='challenge-answer-list-create'),
    path('family-stories/', FamilyStoryListCreateView.as_view(), name='family-story-list-create'),
    path('family-stories/<int:pk>/', FamilyStoryDetailView.as_view(), name='family-story-detail'),
]