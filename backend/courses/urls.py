from django.urls import path

from courses.views import (
    AdminCourseDetailView,
    AdminCourseListCreateView,
    AdminLessonDetailView,
    AdminLessonListCreateView,
    AdminSectionDetailView,
    AdminSectionListCreateView,
    CourseCatalogView,
    CourseDetailView,
)

urlpatterns = [
    path("courses/catalog/", CourseCatalogView.as_view(), name="courses-catalog"),
    path("courses/catalog/<slug:slug>/", CourseDetailView.as_view(), name="course-detail"),
    path("courses/admin/courses/", AdminCourseListCreateView.as_view(), name="admin-courses"),
    path("courses/admin/courses/<int:pk>/", AdminCourseDetailView.as_view(), name="admin-course-detail"),
    path(
        "courses/admin/courses/<int:course_id>/sections/",
        AdminSectionListCreateView.as_view(),
        name="admin-sections",
    ),
    path("courses/admin/sections/<int:pk>/", AdminSectionDetailView.as_view(), name="admin-section-detail"),
    path(
        "courses/admin/sections/<int:section_id>/lessons/",
        AdminLessonListCreateView.as_view(),
        name="admin-lessons",
    ),
    path("courses/admin/lessons/<int:pk>/", AdminLessonDetailView.as_view(), name="admin-lesson-detail"),
]
