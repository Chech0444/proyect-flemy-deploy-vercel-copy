from django.contrib import admin
from django.shortcuts import redirect
from learning.models import Course, Enrollment
from users.models import User, UserRole
from certificates.models import Certificate

# Sobreescribimos el comportamiento del sitio por defecto de Django
# Esto es más seguro que crear uno nuevo ya que evita problemas de registro circular

def get_dynamic_metrics(request):
    return {
        'course_count': Course.objects.count(),
        'student_count': User.objects.exclude(role=UserRole.ADMIN).count(),
        'certificate_count': Certificate.objects.count(),
        'enrollment_count': Enrollment.objects.count(),
    }

# Guardamos la función original
original_index = admin.site.index

def flemy_admin_index(request, extra_context=None):
    if extra_context is None:
        extra_context = {}
    
    # Inyectamos nuestros datos dinámicos
    extra_context.update(get_dynamic_metrics(request))
    
    return original_index(request, extra_context)

# Aplicamos el parche al sitio principal
admin.site.index = flemy_admin_index
admin.site.site_header = "Flemy Dashboard"
admin.site.site_title = "Panel Flemy"
admin.site.index_title = "Gestion general de la plataforma"

def angular_admin_login(request, extra_context=None):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('/admin/')
    return redirect('http://localhost:4200/login')

admin.site.login = angular_admin_login
