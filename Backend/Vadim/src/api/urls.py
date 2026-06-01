from django.urls import path

from .views import HealthView, RegisterView, AuthView, EmailLoginView, LogoutView, MoodEntryListCreateView

urlpatterns = [
    path('health/', HealthView.as_view(), name='health'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/me/', AuthView.as_view(), name='auth_me'),
    path('auth/login/', EmailLoginView.as_view(), name='email_login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path("moods/", MoodEntryListCreateView.as_view(), name="moods"),
]