import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { RouterLink, Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { NgIf, NgFor, KeyValuePipe, NgClass } from '@angular/common';
import { TopbarComponent } from '../shared/topbar/topbar.component';
import { AuthService } from '../shared/auth.service';
import { environment } from '../../environments/environment';

@Component({
  selector: 'app-progress',
  standalone: true,
  imports: [NgIf, NgFor, NgClass, RouterLink, KeyValuePipe, TopbarComponent],
  templateUrl: './progress.component.html',
  styleUrl: './progress.component.css'
})
export class ProgressComponent implements OnInit {
  private http = inject(HttpClient);
  private router = inject(Router);
  private cdr = inject(ChangeDetectorRef);

  progressData: any = null;
  isLoading = true;
  userProfile: any = null;
  isAdmin = false;
  private authService = inject(AuthService);

  ngOnInit() {
    this.isAdmin = this.authService.isAdmin();
    this.loadProgress();
    this.loadProfile();
  }

  loadProfile() {
    this.userProfile = {
      first_name: localStorage.getItem('first_name') || 'Estudiante',
      username: localStorage.getItem('username') || 'Usuario',
      role: localStorage.getItem('role') || 'ROLE_FREE'
    };
  }

  loadProgress() {
    const token = localStorage.getItem('access_token');
    if (!token) {
      this.isLoading = false;
      this.router.navigate(['/login']);
      return;
    }

    this.http.get<any>(`${environment.apiUrl}/gamification/progress/`, {
      headers: { Authorization: `Bearer ${token}` }
    }).subscribe({
      next: (data) => {
        console.log('Progress data loaded:', data);
        this.progressData = data;
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error loading progress:', err);
        this.isLoading = false;
        this.cdr.detectChanges();
        // Ya no redirigimos al login para evitar el bucle de cierre de sesión
      }
    });
  }

  logout(event?: Event) {
    if (event) event.preventDefault();
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    this.router.navigate(['/login']);
  }
}
