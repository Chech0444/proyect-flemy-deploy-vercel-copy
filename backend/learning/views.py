from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.models import Course, Lesson
from courses.serializers import CourseSerializer
from learning.models import Enrollment, LessonProgress
from learning.serializers import EnrollmentSerializer, MyEnrollmentSerializer
from learning.services import compute_course_progress, register_study_event


class EnrollmentCreateView(generics.CreateAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        course = serializer.validated_data["course"]
        if Enrollment.objects.filter(user=self.request.user, course=course).exists():
            raise ValidationError("Ya estas inscrito en este curso.")
        serializer.save(user=self.request.user)


class MyCoursesView(generics.ListAPIView):
    serializer_class = MyEnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Enrollment.objects.filter(user=self.request.user).select_related("course")


class CourseLearningDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, slug):
        course = get_object_or_404(Course, slug=slug, is_published=True)
        if course.is_premium and not request.user.is_premium:
            raise PermissionDenied("Este curso es premium.")
        if not Enrollment.objects.filter(user=request.user, course=course).exists():
            raise PermissionDenied("Debes inscribirte primero.")
        data = CourseSerializer(course).data
        if not request.user.is_premium:
            for section in data["sections"]:
                section["lessons"] = [
                    lesson for lesson in section["lessons"] if not lesson["is_premium"]
                ]
        data["progress_percent"] = compute_course_progress(request.user, course)
        return Response(data)


class CompleteLessonView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, pk=lesson_id)
        if lesson.is_premium and not request.user.is_premium:
            raise PermissionDenied("La leccion es premium.")
        if not Enrollment.objects.filter(user=request.user, course=lesson.section.course).exists():
            raise PermissionDenied("Debes inscribirte en el curso.")
        progress, created = LessonProgress.objects.get_or_create(
            user=request.user, lesson=lesson
        )
        if progress.completed:
            return Response(
                {"detail": "La leccion ya estaba completada."},
                status=status.HTTP_200_OK,
            )
        progress.completed = True
        progress.completed_at = timezone.now()
        progress.save(update_fields=["completed", "completed_at"])
        register_study_event(request.user, lesson)
        return Response({"detail": "Leccion completada correctamente."})


class ProgressSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        enrollments = Enrollment.objects.filter(user=request.user).select_related("course")
        summary = [
            {
                "course_id": enrollment.course_id,
                "course_title": enrollment.course.title,
                "progress_percent": compute_course_progress(request.user, enrollment.course),
            }
            for enrollment in enrollments
        ]
        return Response(summary)
