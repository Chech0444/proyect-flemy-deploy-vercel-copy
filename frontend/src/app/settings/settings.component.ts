import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { TopbarComponent } from '../shared/topbar/topbar.component';
import { SidebarComponent } from '../shared/sidebar/sidebar.component';
import { Router } from '@angular/router';
import { environment } from '../../environments/environment';
import { AuthService } from '../shared/auth.service';
import { NotificationService } from '../shared/notification.service';
 
 @Component({
  selector: 'app-settings',
  standalone: true,
  imports: [CommonModule, FormsModule, TopbarComponent, SidebarComponent],
  templateUrl: './settings.component.html',
  styleUrls: ['./settings.component.css']
})
export class SettingsComponent implements OnInit {
  private http = inject(HttpClient);
  private cdr = inject(ChangeDetectorRef);
  private notificationService = inject(NotificationService);
  private authService = inject(AuthService);

  userProfile: any = null;

  settings = {
    difficulty: 'intermedio',
    languages: ['Python', 'JavaScript', 'TypeScript'],
    interface: {
      language: 'es'
    },
    notifications: {
      browser: false,
      email: true,
      sound: true
    },
    privacy: {
      publicProfile: true,
      searchIndexing: false
    }
  };

  isLoading = true;
  isSaving = false;
  saveSuccess = false;
  isAdmin = false;
  newLanguage = '';

  constructor(private router: Router) {}

  ngOnInit() {
    this.isAdmin = this.authService.isAdmin();
    this.userProfile = {
      first_name: localStorage.getItem('first_name') || 'Estudiante',
      username: localStorage.getItem('username') || 'Usuario',
      role: localStorage.getItem('role') || 'ROLE_FREE',
      photo: null
    };
    this.loadSettings();
  }

  deepMerge(target: any, source: any): any {
    const result = { ...target };
    for (const key of Object.keys(source)) {
      if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
        result[key] = this.deepMerge(target[key] || {}, source[key]);
      } else {
        result[key] = source[key];
      }
    }
    return result;
  }

  loadSettings() {
    const token = localStorage.getItem('access_token');
    if (!token) {
      this.isLoading = false;
      return;
    }

    this.http.get<any>(`${environment.apiUrl}/auth/profile/`, {
      headers: { Authorization: `Bearer ${token}` }
    }).subscribe({
      next: (data) => {
        this.userProfile = data;
        localStorage.setItem('username', data.username || '');
        localStorage.setItem('first_name', data.first_name || '');
        localStorage.setItem('role', data.role || '');
        if (data.preferences && Object.keys(data.preferences).length > 0) {
          this.settings = this.deepMerge(this.settings, data.preferences);
        }
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.isLoading = false;
        this.cdr.detectChanges();
      }
    });
  }

  setDifficulty(level: string) {
    this.settings.difficulty = level;
    this.cdr.detectChanges();
  }

  removeLanguage(lang: string) {
    this.settings.languages = this.settings.languages.filter((l: string) => l !== lang);
    this.cdr.detectChanges();
  }

  addLanguage() {
    const lang = this.newLanguage.trim();
    if (!lang) return;
    if (this.settings.languages.includes(lang)) {
      this.notificationService.showError('Ese lenguaje ya esta agregado.');
      return;
    }
    this.settings.languages.push(lang);
    this.newLanguage = '';
    this.cdr.detectChanges();
  }

  saveSettings() {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    this.isSaving = true;
    this.cdr.detectChanges();
    this.http.patch<any>(`${environment.apiUrl}/auth/profile/`,
      { preferences: this.settings },
      { headers: { Authorization: `Bearer ${token}` } }
    ).subscribe({
      next: () => {
        this.isSaving = false;
        this.saveSuccess = true;
        this.cdr.detectChanges();
        setTimeout(() => {
          this.saveSuccess = false;
          this.cdr.detectChanges();
        }, 3000);
      },
      error: (err) => {
        this.isSaving = false;
        this.cdr.detectChanges();
        this.notificationService.showError(err.error?.detail || 'Error al guardar configuracion');
      }
    });
  }

  discardChanges() {
    this.router.navigate(['/dashboard']);
  }

  logout(event?: Event) {
    if (event) event.preventDefault();
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('username');
    localStorage.removeItem('first_name');
    localStorage.removeItem('role');
    this.router.navigate(['/login']);
  }
}
