from django.contrib.auth import get_user_model
from rest_framework import serializers

from gamification.models import XPTransaction

User = get_user_model()


class XPTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = XPTransaction
        fields = ("id", "amount", "reason", "created_at")


class DashboardSerializer(serializers.ModelSerializer):
    level = serializers.SerializerMethodField()
    recent_transactions = serializers.SerializerMethodField()
    active_enrollments = serializers.SerializerMethodField()
    ai_suggestions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("username", "first_name", "role", "xp", "study_streak", "level", "recent_transactions", "active_enrollments", "ai_suggestions")

    def get_level(self, obj):
        return (obj.xp // 100) + 1

    def get_recent_transactions(self, obj):
        items = obj.xp_transactions.order_by("-created_at")[:10]
        return XPTransactionSerializer(items, many=True).data
        
    def get_active_enrollments(self, obj):
        from learning.serializers import MyEnrollmentSerializer
        enrollments = obj.enrollments.all()[:2] # Limit to 2 for dashboard
        return MyEnrollmentSerializer(enrollments, many=True).data
        
    def get_ai_suggestions(self, obj):
        from courses.models import Course
        from courses.serializers import CourseCatalogSerializer
        # Simple AI suggestion: courses not enrolled in
        enrolled_ids = obj.enrollments.values_list('course_id', flat=True)
        suggested = Course.objects.exclude(id__in=enrolled_ids).order_by('?')[:1]
        return CourseCatalogSerializer(suggested, many=True).data


class LeaderboardSerializer(serializers.ModelSerializer):
    level = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "username", "xp", "study_streak", "level")

    def get_level(self, obj):
        return (obj.xp // 100) + 1
class ProgressDashboardSerializer(serializers.Serializer):
    username = serializers.CharField()
    first_name = serializers.CharField()
    role = serializers.CharField()
    learning_streak = serializers.IntegerField()
    learning_hours = serializers.FloatField()
    avg_quiz_score = serializers.FloatField()
    heatmap_data = serializers.DictField()
    global_progress = serializers.FloatField()
    course_breakdown = serializers.ListField()
    recent_activity = serializers.ListField()
