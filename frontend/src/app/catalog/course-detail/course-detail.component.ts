import { Component, OnInit, inject, ChangeDetectorRef, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

import { environment } from '../../../environments/environment';
import { NotificationService } from '../../shared/notification.service';
import { AuthService } from '../../shared/auth.service';

@Component({
  selector: 'app-course-detail',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './course-detail.component.html',
  styleUrls: ['./course-detail.component.css']
})
export class CourseDetailComponent implements OnInit, OnDestroy {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private http = inject(HttpClient);
  private notificationService = inject(NotificationService);
  private cdr = inject(ChangeDetectorRef);
  private authService = inject(AuthService);

  courseId: string | null = null;
  course: any = null;
  isLoading = true;
  brokenImages: Set<string> = new Set();
  
  // Estado de la UI
  activeTab: 'description' | 'chat' | 'transcription' | 'summary' | 'quiz' = 'description';

  // IA Chat
  aiQuery = '';
  aiResponse = '';
  isAiTyping = false;
  chatMessages: { role: 'user' | 'ai'; text: string }[] = [];

  // ===================================================
  // Estado de Video/IA (nuevo)
  // ===================================================
  isAdmin = false;
  isUploadingVideo = false;
  uploadProgress = 0;

  // Datos de IA de la lección activa
  activeLessonVideoData: any = null;
  processingStatus: any = null;
  transcriptionData: any = null;
  summaryData: any = null;
  quizData: any[] = [];
  
  // Estado del quiz interactivo
  quizAnswers: { [questionId: number]: number } = {};
  quizSubmitted: { [questionId: number]: boolean } = {};
  quizScore = 0;
  quizTotalAnswered = 0;

  // Polling
  private pollingInterval: any = null;

  ngOnInit() {
    this.isAdmin = this.authService.isAdmin();

    this.route.paramMap.subscribe(params => {
      this.courseId = params.get('slug');
      this.loadCourseData();
    });
  }

  ngOnDestroy() {
    this.stopPolling();
  }

  onImageError(key: string) {
    this.brokenImages.add(key);
    this.cdr.detectChanges();
  }

  isImageBroken(key: string): boolean {
    return this.brokenImages.has(key);
  }

  loadCourseData(targetLessonId?: number | null) {
    if (!this.authService.isLoggedIn()) {
      this.isLoading = false;
      this.router.navigate(['/login']);
      return;
    }

    this.http.get<any>(`${environment.apiUrl}/courses/catalog/${this.courseId}/`).subscribe({
      next: (data: any) => {
        this.course = data;
        
        if (!this.course.sections) this.course.sections = [];
        
        // Seleccionar la lección indicada, o la primera por defecto
        let targetLesson: any = null;
        if (targetLessonId) {
          for (const s of this.course.sections) {
            targetLesson = s.lessons?.find((l: any) => l.id === targetLessonId);
            if (targetLesson) break;
          }
        }
        if (!targetLesson && this.course.sections.length > 0 && this.course.sections[0].lessons?.length > 0) {
          targetLesson = this.course.sections[0].lessons[0];
        }
        if (targetLesson) {
          targetLesson.active = true;
          this.loadLessonVideoData(targetLesson.id);
          this.loadChatHistory(targetLesson.id);
        }
        
        this.isLoading = false;
        this.cdr.detectChanges();
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

  // ===================================================
  // Métodos de Video/IA
  // ===================================================

  loadLessonVideoData(lessonId: number) {
    if (!this.authService.isLoggedIn()) return;

    this.activeLessonVideoData = null;
    this.processingStatus = null;
    this.transcriptionData = null;
    this.summaryData = null;
    this.quizData = [];
    this.stopPolling();

    this.http.get<any>(`${environment.apiUrl}/courses/lessons/${lessonId}/video/`).subscribe({
      next: (res) => {
        if (res.data) {
          this.activeLessonVideoData = res.data;
          this.processingStatus = res.data.processing_status;
          this.transcriptionData = res.data.transcription;
          this.summaryData = res.data.summary;
          this.quizData = res.data.quiz_questions || [];
          
          // Cargar estado guardado en localStorage
          const stateKey = `quiz_state_${res.data.id}`;
          const savedStateStr = localStorage.getItem(stateKey);
          if (savedStateStr) {
             try {
                const savedState = JSON.parse(savedStateStr);
                this.quizAnswers = savedState.quizAnswers || {};
                this.quizSubmitted = savedState.quizSubmitted || {};
                this.quizScore = savedState.quizScore || 0;
                this.quizTotalAnswered = savedState.quizTotalAnswered || 0;
             } catch(e) {}
          } else {
             this.quizAnswers = {};
             this.quizSubmitted = {};
             this.quizScore = 0;
             this.quizTotalAnswered = 0;
          }
          
          // Si está procesando, iniciar polling
          if (this.processingStatus && 
              (this.processingStatus.status === 'pending' || this.processingStatus.status === 'processing')) {
            this.startPolling(res.data.id);
          }
        }
        this.cdr.detectChanges();
      },
      error: () => {
        // No hay video, es normal
        this.cdr.detectChanges();
      }
    });
  }

  startPolling(videoId: number) {
    this.stopPolling();
    this.pollingInterval = setInterval(() => {
      if (!this.authService.isLoggedIn()) return;

      this.http.get<any>(`${environment.apiUrl}/courses/videos/${videoId}/status/`).subscribe({
        next: (res) => {
          this.processingStatus = res.data;
          
          if (res.data.status === 'completed') {
            this.stopPolling();
            // Recargar todos los datos
            const activeLesson = this.getActiveLesson();
            if (activeLesson) {
              this.loadLessonVideoData(activeLesson.id);
            }
            this.notificationService.showSuccess('¡Procesamiento de IA completado! 🎉');
          } else if (res.data.status === 'error') {
            this.stopPolling();
            this.notificationService.showError('Error en el procesamiento del video.');
          }
          
          this.cdr.detectChanges();
        }
      });
    }, 3000); // Cada 3 segundos
  }

  stopPolling() {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
      this.pollingInterval = null;
    }
  }

  uploadVideo(event: any) {
    const file = event.target.files[0];
    if (!file) return;

    const activeLesson = this.getActiveLesson();
    if (!activeLesson) {
      this.notificationService.showError('Selecciona una lección primero.');
      return;
    }

    if (!this.authService.isLoggedIn()) return;

    const formData = new FormData();
    formData.append('video_file', file);

    this.isUploadingVideo = true;
    this.uploadProgress = 0;

    this.http.post<any>(
      `${environment.apiUrl}/courses/admin/lessons/${activeLesson.id}/upload-video/`,
      formData,
      { reportProgress: true }
    ).subscribe({
      next: (res) => {
        this.isUploadingVideo = false;
        this.notificationService.showSuccess('Video subido exitosamente. El procesamiento ha iniciado.');
        this.loadLessonVideoData(activeLesson.id);
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.isUploadingVideo = false;
        const msg = err.error?.message || 'Error al subir el video.';
        this.notificationService.showError(msg);
        this.cdr.detectChanges();
      }
    });
  }

  regenerateSummary() {
    if (!this.authService.isLoggedIn() || !this.activeLessonVideoData) return;

    this.http.post<any>(`${environment.apiUrl}/courses/admin/videos/${this.activeLessonVideoData.id}/regenerate-summary/`, {}).subscribe({
      next: (res) => {
        this.notificationService.showSuccess('Regenerando resumen con IA. Puede tardar unos segundos...');
        this.startPolling(this.activeLessonVideoData.id);
      },
      error: (err) => {
        this.notificationService.showError('Error al intentar regenerar el resumen con IA.');
      }
    });
  }

  regenerateQuiz() {
    if (!this.authService.isLoggedIn() || !this.activeLessonVideoData) return;

    this.http.post<any>(`${environment.apiUrl}/courses/admin/videos/${this.activeLessonVideoData.id}/regenerate-quiz/`, {}).subscribe({
      next: (res) => {
        this.notificationService.showSuccess('Regenerando quiz con IA. Puede tardar unos segundos...');
        localStorage.removeItem(`quiz_state_${this.activeLessonVideoData.id}`);
        this.startPolling(this.activeLessonVideoData.id);
      },
      error: (err) => {
        this.notificationService.showError('Error al intentar regenerar el quiz con IA.');
      }
    });
  }

  // ===================================================
  // Métodos de Quiz Interactivo
  // ===================================================

  selectQuizAnswer(questionId: number, optionIndex: number) {
    if (this.quizSubmitted[questionId]) return; // Ya respondida
    this.quizAnswers[questionId] = optionIndex;
    this.cdr.detectChanges();
  }

  submitQuizAnswer(questionId: number) {
    if (this.quizSubmitted[questionId]) return;
    this.quizSubmitted[questionId] = true;
    this.quizTotalAnswered++;

    const question = this.quizData.find((q: any) => q.id === questionId);
    if (question && this.quizAnswers[questionId] === question.correct_option) {
      this.quizScore++;
    }
    
    // Guardar estado
    if (this.activeLessonVideoData) {
       const stateKey = `quiz_state_${this.activeLessonVideoData.id}`;
       localStorage.setItem(stateKey, JSON.stringify({
          quizAnswers: this.quizAnswers,
          quizSubmitted: this.quizSubmitted,
          quizScore: this.quizScore,
          quizTotalAnswered: this.quizTotalAnswered
       }));
    }

    this.cdr.detectChanges();
  }

  isQuizAnswerCorrect(questionId: number): boolean {
    const question = this.quizData.find((q: any) => q.id === questionId);
    return question && this.quizAnswers[questionId] === question.correct_option;
  }

  resetQuiz() {
    this.quizAnswers = {};
    this.quizSubmitted = {};
    this.quizScore = 0;
    this.quizTotalAnswered = 0;
    if (this.activeLessonVideoData) {
        localStorage.removeItem(`quiz_state_${this.activeLessonVideoData.id}`);
    }
    this.cdr.detectChanges();
  }

  // ===================================================
  // Métodos Existentes (preservados)
  // ===================================================

  getActiveLesson(): any {
    if (!this.course?.sections) return null;
    for (const section of this.course.sections) {
      const active = section.lessons?.find((l: any) => l.active);
      if (active) return active;
    }
    return this.course.sections[0]?.lessons?.[0] || null;
  }

  askAi() {
    if (!this.aiQuery.trim() || this.isAiTyping) return;
    
    const activeLesson = this.getActiveLesson();
    if (!activeLesson) {
      this.notificationService.showError('No se pudo determinar la lección actual.');
      return;
    }

    const question = this.aiQuery.trim();
    this.chatMessages.push({ role: 'user', text: question });
    this.aiQuery = '';
    this.isAiTyping = true;
    this.cdr.detectChanges();
    
    this.http.post<any>(`${environment.apiUrl}/ai/chatbot/`, {
      lesson_id: activeLesson.id,
      question: question
    }).subscribe({
      next: (res) => {
        this.chatMessages.push({ role: 'ai', text: res.answer });
        this.isAiTyping = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.chatMessages.push({ role: 'ai', text: 'Lo siento, no pude responder en este momento. Inténtalo de nuevo.' });
        this.isAiTyping = false;
        this.cdr.detectChanges();
      }
    });
  }

  enroll() {
    if (!this.authService.isLoggedIn()) return;

    this.isLoading = true;
    this.http.post(`${environment.apiUrl}/learning/enrollments/`, {
      course: this.course.id
    }).subscribe({
      next: () => {
        this.notificationService.showSuccess('¡Inscripción exitosa! Bienvenido al curso.');
        this.loadCourseData();
      },
      error: (err) => {
        this.isLoading = false;
        const msg = err.error?.detail || 'No se pudo completar la inscripción.';
        this.notificationService.showError(msg);
        this.cdr.detectChanges();
      }
    });
  }

  completeLesson(lessonId: number) {
    if (!this.authService.isLoggedIn()) return;

    // Buscar la siguiente lección para navegar automáticamente
    const lessons = this.getFlatLessons();
    const currentIdx = lessons.findIndex((l: any) => l.id === lessonId);
    const nextLessonId = (currentIdx >= 0 && currentIdx < lessons.length - 1)
      ? lessons[currentIdx + 1].id
      : null;

    this.http.post(`${environment.apiUrl}/learning/lessons/${lessonId}/complete/`, {}).subscribe({
      next: () => {
        this.notificationService.showSuccess('¡Lección completada! Has ganado XP.');
        this.loadCourseData(nextLessonId);
      },
      error: () => {
        this.notificationService.showError('Hubo un problema al marcar la lección.');
      }
    });
  }

  selectLesson(lesson: any) {
    this.course.sections.forEach((section: any) => {
      section.lessons.forEach((l: any) => l.active = false);
    });
    
    lesson.active = true;
    this.aiResponse = '';
    this.chatMessages = [];
    this.activeTab = 'description';
    this.loadLessonVideoData(lesson.id);
    this.loadChatHistory(lesson.id);
    this.notificationService.showSuccess(`Cargando: ${lesson.title}`);
    this.cdr.detectChanges();
  }

  getFlatLessons(): any[] {
    if (!this.course?.sections) return [];
    let lessons: any[] = [];
    this.course.sections.forEach((s: any) => {
      if (s.lessons) lessons = lessons.concat(s.lessons);
    });
    return lessons;
  }

  hasNextClass(): boolean {
    const lessons = this.getFlatLessons();
    const activeIdx = lessons.findIndex((l) => l.active);
    return activeIdx >= 0 && activeIdx < lessons.length - 1;
  }

  nextClass() {
    const lessons = this.getFlatLessons();
    const activeIdx = lessons.findIndex((l) => l.active);
    if (activeIdx >= 0 && activeIdx < lessons.length - 1) {
      this.selectLesson(lessons[activeIdx + 1]);
    }
  }

  selectTab(tab: 'description' | 'chat' | 'transcription' | 'summary' | 'quiz') {
    this.activeTab = tab;
  }

  loadChatHistory(lessonId: number) {
    if (!this.authService.isLoggedIn()) return;

    this.http.get<any[]>(`${environment.apiUrl}/ai/chatbot/?lesson_id=${lessonId}`).subscribe({
      next: (history) => {
        if (history && history.length > 0) {
           this.chatMessages = history;
        }
        this.cdr.detectChanges();
      },
      error: () => {
        console.error('No se pudo cargar el historial del chat');
      }
    });
  }

  goBack() {
    this.router.navigate(['/catalog']);
  }

  formatTimestamp(seconds: number): string {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }
}
