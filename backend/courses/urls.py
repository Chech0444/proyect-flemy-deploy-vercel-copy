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
    CourseSuggestionsView,
    # Video AI views
    VideoUploadView,
    VideoStatusView,
    VideoTranscriptionView,
    VideoSummaryView,
    VideoQuizView,
    LessonVideoDetailView,
    VideoRegenerateSummaryView,
    VideoRegenerateQuizView,
)

urlpatterns = [
    path("courses/catalog/", CourseCatalogView.as_view(), name="courses-catalog"),
    path("courses/catalog/<slug:slug>/", CourseDetailView.as_view(), name="course-detail"),
    path("courses/suggestions/", CourseSuggestionsView.as_view(), name="courses-suggestions"),
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

    # ===================================================
    # Video AI Endpoints
    # ===================================================
    path("courses/admin/lessons/<int:lesson_id>/upload-video/", VideoUploadView.as_view(), name="video-upload"),
    path("courses/videos/<int:video_id>/status/", VideoStatusView.as_view(), name="video-status"),
    path("courses/videos/<int:video_id>/transcription/", VideoTranscriptionView.as_view(), name="video-transcription"),
    path("courses/videos/<int:video_id>/summary/", VideoSummaryView.as_view(), name="video-summary"),
    path("courses/videos/<int:video_id>/quiz/", VideoQuizView.as_view(), name="video-quiz"),
    path("courses/admin/videos/<int:video_id>/regenerate-summary/", VideoRegenerateSummaryView.as_view(), name="video-regenerate-summary"),
    path("courses/admin/videos/<int:video_id>/regenerate-quiz/", VideoRegenerateQuizView.as_view(), name="video-regenerate-quiz"),
    path("courses/lessons/<int:lesson_id>/video/", LessonVideoDetailView.as_view(), name="lesson-video-detail"),
]
