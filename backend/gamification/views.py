from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from learning.models import LessonProgress, Enrollment
from learning.services import compute_course_progress
from gamification.serializers import DashboardSerializer, LeaderboardSerializer, ProgressDashboardSerializer
from certificates.models import Certificate
from certificates.serializers import CertificateSerializer

User = get_user_model()


class DashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(DashboardSerializer(request.user).data)


class ProgressDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # 1. Learning Hours (Sum of completed lesson durations)
        completed_lessons = LessonProgress.objects.filter(user=user, completed=True).select_related('lesson')
        total_minutes = completed_lessons.aggregate(total=Sum('lesson__duration_minutes'))['total'] or 0
        learning_hours = round(total_minutes / 60, 1)
        
        # Weekly learning hours
        week_start = timezone.localdate() - timedelta(days=timezone.localdate().weekday())
        weekly_lessons = completed_lessons.filter(completed_at__date__gte=week_start)
        weekly_minutes = weekly_lessons.aggregate(total=Sum('lesson__duration_minutes'))['total'] or 0
        weekly_hours = round(weekly_minutes / 60, 1)
        
        # 2. Heatmap Data (Last 30 days)
        today = timezone.localdate()
        start_date = today - timedelta(days=29)
        activity = LessonProgress.objects.filter(
            user=user, 
            completed=True, 
            completed_at__date__gte=start_date
        ).values('completed_at__date').annotate(count=Sum('id'))
        
        heatmap = {str(today - timedelta(days=i)): 0 for i in range(30)}
        for entry in activity:
            heatmap[str(entry['completed_at__date'])] = 1
            
        # 3. Global Progress
        enrollments = Enrollment.objects.filter(user=user).select_related('course')
        course_breakdown = []
        total_progress = 0
        for enrollment in enrollments:
            prog = compute_course_progress(user, enrollment.course)
            course_breakdown.append({
                "title": enrollment.course.title,
                "slug": enrollment.course.slug,
                "thumbnail": enrollment.course.thumbnail.url if enrollment.course.thumbnail else None,
                "progress": prog
            })
            total_progress += prog
        
        global_progress = round(total_progress / len(enrollments), 0) if enrollments.exists() else 0
        
        # 4. Recent Activity
        recent = completed_lessons.order_by('-completed_at')[:10]
        recent_list = [{
            "type": "Lección",
            "title": r.lesson.title,
            "time": r.completed_at.strftime("%Y-%m-%d %H:%M"),
            "status": "Completada"
        } for r in recent]

        # 5. XP & Level
        level = (user.xp // 100) + 1
        xp_progress = user.xp % 100

        # 6. Next lesson
        from learning.models import LessonProgress as LP
        best = None
        for enrollment in enrollments:
            course = enrollment.course
            for section in course.sections.all():
                for lesson in section.lessons.all():
                    is_completed = LP.objects.filter(
                        user=user, lesson=lesson, completed=True
                    ).exists()
                    if not is_completed:
                        candidate = {
                            "course_title": course.title,
                            "course_slug": course.slug,
                            "course_thumbnail": (
                                course.thumbnail.url if course.thumbnail else None
                            ),
                            "section_title": section.title,
                            "lesson_title": lesson.title,
                            "lesson_id": lesson.id,
                        }
                        if best is None or (
                            enrollment.created_at
                            > best.get("_enrolled_at", enrollment.created_at)
                        ):
                            best = candidate
                            best["_enrolled_at"] = enrollment.created_at
                        break
        next_lesson = best
        if next_lesson:
            next_lesson.pop("_enrolled_at", None)

        # 7. Certificates
        certificates_qs = Certificate.objects.filter(user=user).select_related("course")
        certificates = CertificateSerializer(certificates_qs, many=True).data

        data = {
            "username": user.username,
            "first_name": user.first_name,
            "role": user.role,
            "xp": user.xp,
            "level": level,
            "xp_progress": xp_progress,
            "learning_streak": user.study_streak,
            "learning_hours": learning_hours,
            "weekly_hours": weekly_hours,
            "avg_quiz_score": 92.5,
            "heatmap_data": heatmap,
            "global_progress": global_progress,
            "course_breakdown": course_breakdown,
            "recent_activity": recent_list,
            "next_lesson": next_lesson,
            "certificates": certificates,
        }
        
        return Response(ProgressDashboardSerializer(data).data)


class LeaderboardView(generics.ListAPIView):
    serializer_class = LeaderboardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.order_by("-xp", "-study_streak", "date_joined")[:20]

from users.permissions import IsAdminRole
from billing.models import Transaction

class AdminDashboardView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        total_users = User.objects.count()
        premium_users = User.objects.filter(role='ROLE_PREMIUM').count()
        total_enrollments = Enrollment.objects.count()
        total_revenue = Transaction.objects.aggregate(total=Sum('amount'))['total'] or 0
        
        # Últimas 5 transacciones
        recent_sales = Transaction.objects.select_related('user').order_by('-created_at')[:5]
        sales_list = [{
            "user": s.user.username,
            "amount": float(s.amount),
            "date": s.created_at.strftime("%Y-%m-%d %H:%M")
        } for s in recent_sales]

        data = {
            "stats": {
                "total_users": total_users,
                "premium_users": premium_users,
                "total_enrollments": total_enrollments,
                "total_revenue": float(total_revenue)
            },
            "recent_sales": sales_list
        }
        return Response(data)
