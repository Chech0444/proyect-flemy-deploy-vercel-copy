from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend

from courses.models import Course, Lesson, Section
from courses.serializers import (
    CourseCatalogSerializer,
    CourseSerializer,
    LessonSerializer,
    SectionSerializer,
    CourseDetailSerializer,
)
from users.permissions import IsAdminRole, IsPremiumUser
from rest_framework.exceptions import PermissionDenied


class CourseCatalogView(generics.ListAPIView):
    queryset = Course.objects.filter(is_published=True).order_by("-created_at")
    serializer_class = CourseCatalogSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'level', 'is_premium']
    search_fields = ['title', 'short_description', 'description']
    ordering_fields = ['price', 'duration_hours', 'created_at']


class CourseDetailView(generics.RetrieveAPIView):
    queryset = Course.objects.filter(is_published=True)
    serializer_class = CourseDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "slug"

    def get_object(self):
        obj = super().get_object()
        # Si el curso es premium y el usuario no, lanzamos error o limitamos
        if obj.is_premium and not (self.request.user.role in ['ROLE_PREMIUM', 'ROLE_ADMIN']):
            raise PermissionDenied("Este curso es exclusivo para usuarios Premium.")
        return obj


class AdminCourseListCreateView(generics.ListCreateAPIView):
    queryset = Course.objects.all().order_by("-created_at")
    serializer_class = CourseSerializer
    permission_classes = [IsAdminRole]


class AdminCourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAdminRole]


class AdminSectionListCreateView(generics.ListCreateAPIView):
    serializer_class = SectionSerializer
    permission_classes = [IsAdminRole]

    def get_queryset(self):
        return Section.objects.filter(course_id=self.kwargs["course_id"])

    def perform_create(self, serializer):
        serializer.save(course_id=self.kwargs["course_id"])


class AdminSectionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = [IsAdminRole]


class AdminLessonListCreateView(generics.ListCreateAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsAdminRole]

    def get_queryset(self):
        return Lesson.objects.filter(section_id=self.kwargs["section_id"])

    def perform_create(self, serializer):
        serializer.save(section_id=self.kwargs["section_id"])


class AdminLessonDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAdminRole]
