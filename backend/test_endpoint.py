import os
import django
import sys
from rest_framework.test import APIClient

sys.path.append(r'c:\Users\USER\Documents\proyecto final\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User

user = User.objects.get(username="admin")
client = APIClient()
client.force_authenticate(user=user)

resp = client.get('/api/v1/gamification/dashboard/')
print("GAMIFICATION DASHBOARD:", resp.json())
