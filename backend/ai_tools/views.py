from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from ai_tools.models import (
    ChatbotLog,
    CodeFeedbackLog,
    ExerciseQuestion,
    ExerciseSet,
    TranscriptionJob,
)
from ai_tools.serializers import (
    ChatbotSerializer,
    CodeFeedbackSerializer,
    ExerciseSetSerializer,
    TranscriptionSerializer,
)
from ai_tools.services import (
    generate_chatbot_answer,
    generate_code_feedback,
    generate_exercise_payload,
    generate_transcription_text,
)
from courses.models import Lesson
from users.permissions import IsAdminRole


def _validate_lesson_access(user, lesson):
    if lesson.is_premium and not user.is_premium:
        raise PermissionDenied("La leccion es premium.")


class TranscriptionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        lesson = get_object_or_404(Lesson, pk=request.data.get("lesson"))
        _validate_lesson_access(request.user, lesson)
        obj = TranscriptionJob.objects.create(
            lesson=lesson, transcript=generate_transcription_text(lesson)
        )
        return Response(TranscriptionSerializer(obj).data)


class ExerciseGenerationView(APIView):
    permission_classes = [IsAdminRole]

    def post(self, request):
        lesson = get_object_or_404(Lesson, pk=request.data.get("lesson"))
        exercise_set = ExerciseSet.objects.create(
            lesson=lesson,
            prompt_context=request.data.get("prompt_context", lesson.content),
            created_by=request.user,
        )
        for item in generate_exercise_payload(lesson):
            ExerciseQuestion.objects.create(exercise_set=exercise_set, **item)
        return Response(ExerciseSetSerializer(exercise_set).data)


class CodeFeedbackView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CodeFeedbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lesson = get_object_or_404(Lesson, pk=serializer.validated_data["lesson_id"])
        _validate_lesson_access(request.user, lesson)
        feedback = generate_code_feedback(
            serializer.validated_data["language"], serializer.validated_data["code"]
        )
        CodeFeedbackLog.objects.create(
            user=request.user,
            lesson=lesson,
            language=serializer.validated_data["language"],
            code=serializer.validated_data["code"],
            feedback=feedback,
        )
        return Response({"feedback": feedback})


class ChatbotView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChatbotSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lesson = get_object_or_404(Lesson, pk=serializer.validated_data["lesson_id"])
        _validate_lesson_access(request.user, lesson)
        answer = generate_chatbot_answer(lesson, serializer.validated_data["question"])
        ChatbotLog.objects.create(
            user=request.user,
            lesson=lesson,
            question=serializer.validated_data["question"],
            answer=answer,
        )
        return Response({"answer": answer})
