from django.contrib import admin

from ai_tools.models import (
    ChatbotLog,
    CodeFeedbackLog,
    ExerciseQuestion,
    ExerciseSet,
    TranscriptionJob,
)


admin.site.register(TranscriptionJob)
admin.site.register(ExerciseSet)
admin.site.register(ExerciseQuestion)
admin.site.register(CodeFeedbackLog)
admin.site.register(ChatbotLog)
