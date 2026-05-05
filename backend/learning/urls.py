from django.urls import path

from learning.views import (
    CompleteLessonView,
    CourseLearningDetailView,
    EnrollmentCreateView,
    MyCoursesView,
    ProgressSummaryView,
)

urlpatterns = [
    path("enrollments/", EnrollmentCreateView.as_view(), name="enrollment-create"),
    path("my-courses/", MyCoursesView.as_view(), name="my-courses"),
    path("courses/<slug:slug>/", CourseLearningDetailView.as_view(), name="course-learning-detail"),
    path("lessons/<int:lesson_id>/complete/", CompleteLessonView.as_view(), name="complete-lesson"),
    path("progress/summary/", ProgressSummaryView.as_view(), name="progress-summary"),
]
