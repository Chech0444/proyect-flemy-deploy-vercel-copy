from datetime import timedelta

from django.utils import timezone

from courses.models import Course
from gamification.models import XPTransaction
from learning.models import LessonProgress


def compute_course_progress(user, course: Course) -> float:
    lesson_ids = list(
        course.sections.prefetch_related("lessons")
        .values_list("lessons__id", flat=True)
    )
    lesson_ids = [lesson_id for lesson_id in lesson_ids if lesson_id]
    if not lesson_ids:
        return 0
    completed = LessonProgress.objects.filter(
        user=user, lesson_id__in=lesson_ids, completed=True
    ).count()
    return round((completed / len(lesson_ids)) * 100, 2)


def update_streak(user):
    today = timezone.localdate()
    if user.last_study_date == today:
        return
    
    yesterday = today - timedelta(days=1)
    if user.last_study_date == yesterday:
        user.study_streak += 1
    else:
        user.study_streak = 1
    
    user.last_study_date = today
    user.save(update_fields=["study_streak", "last_study_date"])

def register_study_event(user, lesson):
    update_streak(user)
    user.xp += 20
    user.save(update_fields=["xp"])
    XPTransaction.objects.create(user=user, amount=20, reason=f"Leccion completada: {lesson.title}")


def check_and_create_notifications(user):
    from users.models import Notification, NotificationType, UserRole
    # Generar sugerencia de IA
    from courses.models import Course
    enrolled_ids = user.enrollments.values_list('course_id', flat=True)
    suggested = Course.objects.exclude(id__in=enrolled_ids).order_by('?').first()
    if suggested:
        Notification.objects.get_or_create(
            user=user, 
            type=NotificationType.SUGGESTION, 
            title="Sugerencia de nuestra IA",
            message=f"Basado en tus intereses, te recomendamos el curso: {suggested.title}",
            action_url=f"/catalog/{suggested.slug}"
        )
    
    # Hito de Racha
    if user.study_streak > 0 and user.study_streak % 5 == 0:
        Notification.objects.get_or_create(
            user=user,
            type=NotificationType.STREAK,
            title="¡Racha increíble!",
            message=f"Has alcanzado una racha de {user.study_streak} días seguidos. ¡Sigue así!",
            action_url="/progreso"
        )

def daily_login_check(user):
    """
    Check if the user hasn't logged in today.
    Grant a small XP bonus for daily login and maintain streak.
    """
    check_and_create_notifications(user)
    
    today = timezone.localdate()
    if user.last_study_date == today:
        return
        
    update_streak(user)
    user.xp += 5
    user.save(update_fields=["xp"])
    XPTransaction.objects.create(user=user, amount=5, reason="Bono por inicio de sesión diario")
