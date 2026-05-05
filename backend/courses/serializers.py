from rest_framework import serializers

from courses.models import Course, Lesson, Section


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = (
            "id",
            "section",
            "title",
            "content",
            "video_url",
            "is_premium",
            "order",
            "duration_minutes",
        )
        read_only_fields = ("section",)


class SectionSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Section
        fields = ("id", "course", "title", "order", "lessons")
        read_only_fields = ("course",)


class CourseSerializer(serializers.ModelSerializer):
    sections = SectionSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = (
            "id",
            "title",
            "slug",
            "short_description",
            "description",
            "thumbnail",
            "is_premium",
            "is_published",
            "created_at",
            "updated_at",
            "sections",
        )


class CourseCatalogSerializer(serializers.ModelSerializer):
    sections_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            "id",
            "title",
            "slug",
            "short_description",
            "thumbnail",
            "is_premium",
            "duration_hours",
            "sections_count",
        )

    def get_sections_count(self, obj):
        return obj.sections.count()


class CourseDetailSerializer(serializers.ModelSerializer):
    sections = SectionSerializer(many=True, read_only=True)
    is_enrolled = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            "id",
            "title",
            "slug",
            "short_description",
            "description",
            "thumbnail",
            "is_premium",
            "duration_hours",
            "sections",
            "is_enrolled",
        )

    def get_is_enrolled(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        from learning.models import Enrollment
        return Enrollment.objects.filter(user=user, course=obj).exists()
