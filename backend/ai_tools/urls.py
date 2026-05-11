from django.urls import path

from ai_tools.views import (
    ChatbotView,
    CodeFeedbackView,
    ExerciseGenerationView,
    TranscriptionView,
)

urlpatterns = [
    path("ai/transcriptions/", TranscriptionView.as_view(), name="ai-transcriptions"),
    path("ai/exercises/", ExerciseGenerationView.as_view(), name="ai-exercises"),
    path("ai/code-feedback/", CodeFeedbackView.as_view(), name="ai-code-feedback"),
    path("ai/chatbot/", ChatbotView.as_view(), name="ai-chatbot"),
]
