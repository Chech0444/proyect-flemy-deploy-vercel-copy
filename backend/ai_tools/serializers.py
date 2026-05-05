from rest_framework import serializers

from ai_tools.models import ExerciseQuestion, ExerciseSet, TranscriptionJob


class TranscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TranscriptionJob
        fields = ("id", "lesson", "transcript", "created_at")
        read_only_fields = ("transcript", "created_at")


class ExerciseQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExerciseQuestion
        fields = ("id", "question", "hint")


class ExerciseSetSerializer(serializers.ModelSerializer):
    questions = ExerciseQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = ExerciseSet
        fields = ("id", "lesson", "prompt_context", "questions", "created_at")


class CodeFeedbackSerializer(serializers.Serializer):
    lesson_id = serializers.IntegerField()
    language = serializers.CharField(max_length=50)
    code = serializers.CharField()


class ChatbotSerializer(serializers.Serializer):
    lesson_id = serializers.IntegerField()
    question = serializers.CharField()
