import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { TopbarComponent } from '../shared/topbar/topbar.component';
import { Router, RouterLink } from '@angular/router';
import { environment } from '../../environments/environment';

@Component({
  selector: 'app-settings',
  standalone: true,
  imports: [CommonModule, FormsModule, TopbarComponent, RouterLink],
  templateUrl: './settings.component.html',
  styleUrls: ['./settings.component.css']
})
export class SettingsComponent implements OnInit {
  private http = inject(HttpClient);
  private cdr = inject(ChangeDetectorRef);
  
  userProfile: any = null;

  // Estructura por defecto
  settings = {
    difficulty: 'intermedio',
    languages: ['Python', 'JavaScript', 'TypeScript'],
    interface: {
      language: 'es',
      fontSize: 50,
      highContrast: false
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

  constructor(private router: Router) {}

  ngOnInit() {
    this.userProfile = {
      first_name: localStorage.getItem('first_name') || 'Estudiante',
      username: localStorage.getItem('username') || 'Usuario',
      role: localStorage.getItem('role') || 'ROLE_FREE',
      photo: null
    };
    this.loadSettings();
  }

  loadSettings() {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    this.http.get<any>(`${environment.apiUrl}/auth/profile/`, {
      headers: { Authorization: `Bearer ${token}` }
    }).subscribe({
      next: (data) => {
        if (data.preferences && Object.keys(data.preferences).length > 0) {
          // Merge deep of settings object with existing default keys to avoid undefined properties
          this.settings = { ...this.settings, ...data.preferences };
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
    if (!this.settings.languages.includes('Java')) {
      this.settings.languages.push('Java');
      this.cdr.detectChanges();
    }
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
      error: () => {
        this.isSaving = false;
        this.cdr.detectChanges();
        alert('Error al guardar configuración');
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
    this.router.navigate(['/login']);
  }
}

