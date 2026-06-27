import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { environment } from '../../environments/environment';
import { TopbarComponent } from '../shared/topbar/topbar.component';
import { NotificationService } from '../shared/notification.service';

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule, TopbarComponent, FormsModule],
  templateUrl: './admin-dashboard.component.html',
  styleUrls: ['./admin-dashboard.component.css']
})
export class AdminDashboardComponent implements OnInit {
  private http = inject(HttpClient);
  private notificationService = inject(NotificationService);
  private cdr = inject(ChangeDetectorRef);

  // --- Stats State ---
  kpiData: any = null;
  courseStats: any = null;
  recentSales: any[] = [];
  userGrowth: number[] = [];
  revenueGrowth: number[] = [];
  activityData: number[] = [];
  isLoadingStats = true;
  statsError = false;

  // Tabs
  activeTab = 'stats';

  // --- Course Management State ---
  courses: any[] = [];
  selectedCourse: any = null;
  sections: any[] = [];
  selectedSection: any = null;
  lessons: any[] = [];
  isCourseModalOpen = false;
  isSectionModalOpen = false;
  isLessonModalOpen = false;
  newCourse: any = { id: null, title: '', slug: '', short_description: '', description: '', level: 'Básico', is_premium: false, is_published: false };
  newSection: any = { id: null, title: '', order: 1 };
  newLesson: any = { id: null, title: '', content: '', order: 1, is_premium: false, video_url: 'http://localhost/dummy' };
  courseFile: File | null = null;
  lessonVideoFile: File | null = null;
  isUploadingVideo = false;

  // Month labels for charts
  months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
  last12Months: string[] = [];

  ngOnInit() {
    this.last12Months = this.generateLast12Months();
    this.loadStats();
    this.loadCourses();
  }

  get authHeaders() {
    return { headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` } };
  }

  switchTab(tab: string) {
    this.activeTab = tab;
  }

  generateLast12Months(): string[] {
    const result: string[] = [];
    const now = new Date();
    for (let i = 11; i >= 0; i--) {
      const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
      result.push(this.months[d.getMonth()]);
    }
    return result;
  }

  // ==========================================
  // STATS — HELPERS
  // ==========================================
  formatCurrency(value: number): string {
    return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'USD', minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(value);
  }

  percChange(current: number, previous: number): string {
    if (previous === 0) return current > 0 ? '+100%' : '0%';
    const change = ((current - previous) / previous) * 100;
    return (change >= 0 ? '+' : '') + change.toFixed(1) + '%';
  }

  percClass(change: string): string {
    return change.startsWith('+') ? 'text-emerald-400' : 'text-red-400';
  }

  percIcon(change: string): string {
    return change.startsWith('+') ? 'trending_up' : 'trending_down';
  }

  // ==========================================
  // STATS — LOAD
  // ==========================================
  loadStats() {
    this.isLoadingStats = true;
    this.statsError = false;
    this.http.get<any>(`${environment.apiUrl}/gamification/admin-stats/`, this.authHeaders).subscribe({
      next: (data) => {
        this.kpiData = data.kpis;
        this.courseStats = data.courses;
        this.userGrowth = data.charts.user_growth;
        this.revenueGrowth = data.charts.revenue_growth;
        this.activityData = data.charts.activity_30d;
        this.recentSales = data.recent_sales || [];
        this.isLoadingStats = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.isLoadingStats = false;
        this.statsError = true;
        this.kpiData = null;
        this.cdr.detectChanges();
      }
    });
  }

  retryStats() {
    this.loadStats();
  }

  // ==========================================
  // COURSES
  // ==========================================
  loadCourses() {
    this.http.get<any[]>(`${environment.apiUrl}/courses/admin/courses/`, this.authHeaders).subscribe(res => {
      this.courses = res;
    });
  }

  openCourseModal(course: any = null) {
    this.courseFile = null;
    if (course) {
      this.newCourse = { ...course };
    } else {
      this.newCourse = { id: null, title: '', slug: '', short_description: '', description: '', level: 'Básico', is_premium: false, is_published: false };
    }
    this.isCourseModalOpen = true;
  }

  onCourseImageSelected(event: any) {
    if (event.target.files.length > 0) {
      this.courseFile = event.target.files[0];
    }
  }

  saveCourse() {
    const isEditing = !!this.newCourse.id;
    const formData = new FormData();
    formData.append('title', this.newCourse.title);
    formData.append('slug', this.newCourse.slug);
    formData.append('short_description', this.newCourse.short_description);
    formData.append('description', this.newCourse.description);
    formData.append('level', this.newCourse.level || 'Básico');
    formData.append('is_premium', this.newCourse.is_premium ? 'true' : 'false');
    formData.append('is_published', this.newCourse.is_published ? 'true' : 'false');
    if (this.courseFile) formData.append('thumbnail', this.courseFile);
    const req = isEditing
      ? this.http.put(`${environment.apiUrl}/courses/admin/courses/${this.newCourse.id}/`, formData, this.authHeaders)
      : this.http.post(`${environment.apiUrl}/courses/admin/courses/`, formData, this.authHeaders);
    req.subscribe({
      next: () => {
        this.notificationService.showSuccess(isEditing ? 'Curso actualizado' : 'Curso creado');
        this.isCourseModalOpen = false;
        this.loadCourses();
        if (isEditing && this.selectedCourse?.id === this.newCourse.id) this.selectCourse({ ...this.newCourse });
      },
      error: () => this.notificationService.showError('Error al guardar el curso')
    });
  }

  deleteCourse(id: number) {
    if (!confirm('¿Estás seguro de eliminar este curso?')) return;
    this.http.delete(`${environment.apiUrl}/courses/admin/courses/${id}/`, this.authHeaders).subscribe(() => {
      this.notificationService.showSuccess('Curso eliminado');
      this.selectedCourse = null;
      this.loadCourses();
    });
  }

  selectCourse(course: any) {
    this.selectedCourse = course;
    this.selectedSection = null;
    this.sections = [];
    this.lessons = [];
    this.loadSections(course.id);
  }

  loadSections(courseId: number) {
    this.http.get<any[]>(`${environment.apiUrl}/courses/admin/courses/${courseId}/sections/`, this.authHeaders).subscribe(res => { this.sections = res; });
  }

  openSectionModal(section: any = null) {
    if (section) { this.newSection = { ...section }; }
    else { this.newSection = { id: null, title: '', order: this.sections.length + 1 }; }
    this.isSectionModalOpen = true;
  }

  saveSection() {
    if (!this.selectedCourse) return;
    const isEditing = !!this.newSection.id;
    const req = isEditing
      ? this.http.put(`${environment.apiUrl}/courses/admin/sections/${this.newSection.id}/`, this.newSection, this.authHeaders)
      : this.http.post(`${environment.apiUrl}/courses/admin/courses/${this.selectedCourse.id}/sections/`, this.newSection, this.authHeaders);
    req.subscribe({
      next: () => {
        this.notificationService.showSuccess(isEditing ? 'Sección actualizada' : 'Sección creada');
        this.isSectionModalOpen = false;
        this.loadSections(this.selectedCourse.id);
        if (isEditing && this.selectedSection?.id === this.newSection.id) this.selectSection({ ...this.newSection, course: this.selectedCourse.id });
      },
      error: () => this.notificationService.showError('Error al guardar la sección')
    });
  }

  deleteSection(id: number) {
    if (!confirm('¿Seguro de eliminar esta sección?')) return;
    this.http.delete(`${environment.apiUrl}/courses/admin/sections/${id}/`, this.authHeaders).subscribe(() => {
      this.notificationService.showSuccess('Sección eliminada');
      this.selectedSection = null;
      this.loadSections(this.selectedCourse.id);
    });
  }

  selectSection(section: any) {
    this.selectedSection = section;
    this.lessons = [];
    this.loadLessons(section.id);
  }

  loadLessons(sectionId: number) {
    this.http.get<any[]>(`${environment.apiUrl}/courses/admin/sections/${sectionId}/lessons/`, this.authHeaders).subscribe(res => { this.lessons = res; });
  }

  openLessonModal(lesson: any = null) {
    this.lessonVideoFile = null;
    this.isUploadingVideo = false;
    if (lesson) { this.newLesson = { ...lesson }; }
    else { this.newLesson = { id: null, title: '', content: '', order: this.lessons.length + 1, is_premium: false, video_url: 'http://localhost/dummy' }; }
    this.isLessonModalOpen = true;
  }

  onLessonVideoSelected(event: any) {
    if (event.target.files.length > 0) this.lessonVideoFile = event.target.files[0];
  }

  saveLesson() {
    if (!this.selectedSection) return;
    const isEditing = !!this.newLesson.id;
    if (!this.newLesson.video_url) this.newLesson.video_url = 'http://localhost/dummy';
    const req = isEditing
      ? this.http.put<any>(`${environment.apiUrl}/courses/admin/lessons/${this.newLesson.id}/`, this.newLesson, this.authHeaders)
      : this.http.post<any>(`${environment.apiUrl}/courses/admin/sections/${this.selectedSection.id}/lessons/`, this.newLesson, this.authHeaders);
    req.subscribe({
      next: (savedLesson) => {
        if (this.lessonVideoFile) {
          this.isUploadingVideo = true;
          const videoFormData = new FormData();
          videoFormData.append('video_file', this.lessonVideoFile);
          this.http.post(`${environment.apiUrl}/courses/admin/lessons/${savedLesson.id}/upload-video/`, videoFormData, this.authHeaders).subscribe({
            next: () => {
              this.isUploadingVideo = false;
              this.notificationService.showSuccess('Lección guardada y video subido para procesar IA');
              this.isLessonModalOpen = false;
              this.loadLessons(this.selectedSection.id);
            },
            error: () => {
              this.isUploadingVideo = false;
              this.notificationService.showError('Lección guardada, pero hubo un error al subir el video');
              this.isLessonModalOpen = false;
              this.loadLessons(this.selectedSection.id);
            }
          });
        } else {
          this.notificationService.showSuccess(isEditing ? 'Lección actualizada' : 'Lección creada');
          this.isLessonModalOpen = false;
          this.loadLessons(this.selectedSection.id);
        }
      },
      error: () => this.notificationService.showError('Error al guardar la lección')
    });
  }

  deleteLesson(id: number) {
    if (!confirm('¿Seguro de eliminar esta lección?')) return;
    this.http.delete(`${environment.apiUrl}/courses/admin/lessons/${id}/`, this.authHeaders).subscribe(() => {
      this.notificationService.showSuccess('Lección eliminada');
      this.loadLessons(this.selectedSection.id);
    });
  }
}
