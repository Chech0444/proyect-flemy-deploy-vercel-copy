from django.urls import path

from gamification.views import DashboardView, LeaderboardView, ProgressDashboardView, AdminDashboardView

urlpatterns = [
    path("dashboard/", DashboardView.as_view(), name="gamification-dashboard"),
    path("progress/", ProgressDashboardView.as_view(), name="gamification-progress"),
    path("leaderboard/", LeaderboardView.as_view(), name="gamification-leaderboard"),
    path("admin-stats/", AdminDashboardView.as_view(), name="admin-stats"),
]
