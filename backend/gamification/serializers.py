from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import Sum
from rest_framework import serializers

from gamification.models import XPTransaction

User = get_user_model()


class XPTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = XPTransaction
        fields = ("id", "amount", "reason", "created_at")


class DashboardSerializer(serializers.ModelSerializer):
    level = serializers.SerializerMethodField()
    xp_progress = serializers.SerializerMethodField()
    recent_transactions = serializers.SerializerMethodField()
    active_enrollments = serializers.SerializerMethodField()
    total_enrollments = serializers.SerializerMethodField()
    learning_hours = serializers.SerializerMethodField()
    global_progress = serializers.SerializerMethodField()
    recent_activity = serializers.SerializerMethodField()
    ai_suggestions = serializers.SerializerMethodField()
    heatmap_data = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "username", "first_name", "role",
            "xp", "study_streak", "level", "xp_progress",
            "recent_transactions", "active_enrollments",
            "total_enrollments", "learning_hours",
            "global_progress", "recent_activity",
            "ai_suggestions", "heatmap_data",
        )

    def get_level(self, obj):
        return (obj.xp // 100) + 1

    def get_xp_progress(self, obj):
        return obj.xp % 100

    def get_recent_transactions(self, obj):
        items = obj.xp_transactions.order_by("-created_at")[:10]
        return XPTransactionSerializer(items, many=True).data

    def get_active_enrollments(self, obj):
        from learning.serializers import MyEnrollmentSerializer
        enrollments = obj.enrollments.prefetch_related(
            "course__sections__lessons"
        ).all()[:6]
        return MyEnrollmentSerializer(enrollments, many=True).data

    def get_total_enrollments(self, obj):
        return obj.enrollments.count()

    def get_learning_hours(self, obj):
        from learning.models import LessonProgress
        completed = LessonProgress.objects.filter(
            user=obj, completed=True
        ).select_related("lesson")
        total_minutes = completed.aggregate(total=Sum("lesson__duration_minutes"))["total"] or 0
        return round(total_minutes / 60, 1)

    def get_global_progress(self, obj):
        enrollments = obj.enrollments.select_related("course").all()
        if not enrollments:
            return 0
        from learning.services import compute_course_progress
        total = 0
        for e in enrollments:
            total += compute_course_progress(obj, e.course)
        return round(total / len(enrollments), 0)

    def get_recent_activity(self, obj):
        from learning.models import LessonProgress
        recent = LessonProgress.objects.filter(
            user=obj, completed=True
        ).select_related("lesson").order_by("-completed_at")[:5]
        return [{
            "type": "Lección",
            "title": r.lesson.title,
            "time": r.completed_at.strftime("%Y-%m-%d %H:%M") if r.completed_at else "",
            "status": "Completada",
        } for r in recent]

    def get_heatmap_data(self, obj):
        from learning.models import LessonProgress
        today = timezone.localdate()
        start_date = today - timedelta(days=29)
        activity = LessonProgress.objects.filter(
            user=obj, completed=True, completed_at__date__gte=start_date
        ).values("completed_at__date")
        heatmap = {str(today - timedelta(days=i)): 0 for i in range(30)}
        for entry in activity:
            heatmap[str(entry["completed_at__date"])] = 1
        return heatmap

    def get_ai_suggestions(self, obj):
        from courses.models import Course
        from courses.serializers import CourseCatalogSerializer
        enrolled_ids = obj.enrollments.values_list("course_id", flat=True)
        suggested = Course.objects.exclude(id__in=enrolled_ids).order_by("?")[:3]
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
