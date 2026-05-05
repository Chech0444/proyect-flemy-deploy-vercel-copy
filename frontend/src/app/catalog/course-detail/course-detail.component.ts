import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

import { environment } from '../../../environments/environment';
import { NotificationService } from '../../shared/notification.service';

@Component({
  selector: 'app-course-detail',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './course-detail.component.html',
  styleUrls: ['./course-detail.component.css']
})
export class CourseDetailComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private http = inject(HttpClient);
  private notificationService = inject(NotificationService);

  courseId: string | null = null;
  // Estado de la UI según la imagen
  activeTab: 'description' | 'chat' | 'transcription' | 'editor' = 'description';
  
  // Editor de Código
  codeContent = `# Ejercicio: Implementación de Red Neuronal Básica\nimport numpy as np\n\ndef sigmoid(x):\n    return 1 / (1 + np.exp(-x))\n\n# Inicialización de pesos\ninputs = np.array([0.5, -0.2, 0.1])\nweights = np.array([0.4, 0.7, -0.3])\nbias = 0.1\n\n# Calculando la salida\noutput = sigmoid(np.dot(inputs, weights) + bias)\nprint("Resultado de la activación:", output)`;
  outputContent = '';
  isExecutingCode = false;

  // Pantallas Simuladas interactuando con AI
  aiQuery = '';
  aiResponse = '';
  isAiTyping = false;

  ngOnInit() {
    this.route.paramMap.subscribe(params => {
      this.courseId = params.get('slug');
      this.loadCourseData();
    });
  }

  loadCourseData() {
    const token = localStorage.getItem('access_token');
    if (!token) {
      this.isLoading = false;
      this.router.navigate(['/login']);
      return;
    }

    // Obtener detalles desde la base de datos real
    this.http.get<any>(`${environment.apiUrl}/courses/catalog/${this.courseId}/`, {
      headers: { Authorization: `Bearer ${token}` }
    }).subscribe({
      next: (data: any) => {
        this.course = data;
        
        // Verificación de seguridad para evitar errores si no hay contenido
        if (!this.course.sections) this.course.sections = [];
        
        // Seleccionar la primera lección como activa por defecto si existe
        if (this.course.sections.length > 0 && this.course.sections[0].lessons?.length > 0) {
          this.course.sections[0].lessons[0].active = true;
        }
        
        this.isLoading = false;
      },
      error: (err) => {
        if (err.status === 403) {
          this.notificationService.showError('Este curso es exclusivo para miembros Premium. ¡Únete ahora para desbloquearlo!');
          this.router.navigate(['/subscription']);
        } else {
          this.notificationService.showError('Este curso aún no está disponible o no existe.');
          this.router.navigate(['/catalog']);
        }
      }
    });
  }

  askAi() {
    if (!this.aiQuery.trim()) return;
    
    // Buscar la lección activa para dar contexto a la IA
    let activeLessonId = null;
    for (const section of this.course.sections) {
      const active = section.lessons.find((l: any) => l.active);
      if (active) {
        activeLessonId = active.id;
        break;
      }
    }

    // Si no hay ninguna marcada como activa, usamos la primera disponible
    if (!activeLessonId && this.course.sections[0]?.lessons[0]) {
      activeLessonId = this.course.sections[0].lessons[0].id;
    }

    if (!activeLessonId) {
      this.notificationService.showError('No se pudo determinar la lección actual.');
      return;
    }

    this.isAiTyping = true;
    const token = localStorage.getItem('access_token');
    
    this.http.post<any>(`${environment.apiUrl}/ai/chatbot/`, {
      lesson_id: activeLessonId,
      question: this.aiQuery
    }, {
      headers: { Authorization: `Bearer ${token}` }
    }).subscribe({
      next: (res) => {
        this.aiResponse = res.answer;
        this.isAiTyping = false;
        this.aiQuery = '';
      },
      error: () => {
        this.notificationService.showError('El tutor IA no pudo responder en este momento.');
        this.isAiTyping = false;
      }
    });
  }

  enroll() {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    this.isLoading = true;
    this.http.post(`${environment.apiUrl}/learning/enrollments/`, {
      course: this.course.id
    }, {
      headers: { Authorization: `Bearer ${token}` }
    }).subscribe({
      next: () => {
        this.notificationService.showSuccess('¡Inscripción exitosa! Bienvenido al curso.');
        this.loadCourseData(); // Recargar para mostrar el reproductor
      },
      error: (err) => {
        this.isLoading = false;
        const msg = err.error?.detail || 'No se pudo completar la inscripción.';
        this.notificationService.showError(msg);
      }
    });
  }

  selectLesson(lesson: any) {
    // Desactivar todas las lecciones en todas las secciones
    this.course.sections.forEach((section: any) => {
      section.lessons.forEach((l: any) => l.active = false);
    });
    
    // Activar la seleccionada
    lesson.active = true;
    this.aiResponse = ''; // Limpiar respuesta IA al cambiar de tema
    this.notificationService.showSuccess(`Cargando: ${lesson.title}`);
  }

  selectTab(tab: 'description' | 'chat' | 'transcription' | 'editor') {
    this.activeTab = tab;
  }

  runCode() {
    this.isExecutingCode = true;
    this.outputContent = 'Ejecutando...';
    
    // Simulación de ejecución con feedback de IA
    setTimeout(() => {
      this.http.post<any>(`${environment.apiUrl}/ai/code-feedback/`, {
        language: 'python',
        code: this.codeContent
      }, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      }).subscribe({
        next: (res) => {
          this.outputContent = `> Resultado de la activación: 0.5841905243301777\n\n[IA FEEDBACK]: ${res.feedback}`;
          this.isExecutingCode = false;
        },
        error: () => {
          this.outputContent = '> Resultado de la activación: 0.5841905243301777\n\n[Error al obtener feedback de IA]';
          this.isExecutingCode = false;
        }
      });
    }, 1500);
  }

  goBack() {
    this.router.navigate(['/catalog']);
  }
}
