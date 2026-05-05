from rest_framework import serializers

from courses.serializers import CourseSerializer
from learning.models import Enrollment, LessonProgress


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ("id", "course", "created_at")
        read_only_fields = ("created_at",)


class LessonProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonProgress
        fields = ("id", "lesson", "completed", "completed_at")


class MyEnrollmentSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    progress_percent = serializers.SerializerMethodField()

    class Meta:
        model = Enrollment
        fields = ("id", "course", "created_at", "progress_percent")

    def get_progress_percent(self, obj):
        total_lessons = obj.course.sections.prefetch_related("lessons")
        lesson_ids = [lesson.id for section in total_lessons for lesson in section.lessons.all()]
        if not lesson_ids:
            return 0
        completed = LessonProgress.objects.filter(
            user=obj.user, lesson_id__in=lesson_ids, completed=True
        ).count()
        return round((completed / len(lesson_ids)) * 100, 2)
