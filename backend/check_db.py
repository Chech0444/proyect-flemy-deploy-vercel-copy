import os
import django
import sys

# Setup Django environment
sys.path.append(r'c:\Users\USER\Documents\proyecto final\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from courses.models import Course
from users.models import User, Notification
from gamification.models import XPTransaction
from learning.services import check_and_create_notifications, daily_login_check

print("--- DIAGNOSTICO DE BASE DE DATOS ---")
courses = Course.objects.all()
print(f"Cursos en base de datos: {courses.count()}")
for c in courses:
    print(f"- {c.title}")

users = User.objects.all()
print(f"Usuarios en base de datos: {users.count()}")
if users.exists():
    test_user = users.first()
    print(f"Probando notificaciones para usuario: {test_user.username}")
    daily_login_check(test_user)
    notifs = Notification.objects.filter(user=test_user)
    print(f"Notificaciones generadas para {test_user.username}: {notifs.count()}")
    for n in notifs:
        print(f"[{n.type}] {n.title} - {n.message}")

print("--- FIN ---")
