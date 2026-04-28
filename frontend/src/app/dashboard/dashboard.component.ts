import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { RouterLink, Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { NgIf, NgFor } from '@angular/common';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [NgIf, NgFor, RouterLink],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css'
})
export class DashboardComponent implements OnInit {
  private http = inject(HttpClient);
  private router = inject(Router);
  private cdr = inject(ChangeDetectorRef);

  userProfile: any = null;
  isLoading = true;

  ngOnInit() {
    this.loadProfile();
  }

  loadProfile() {
    const token = localStorage.getItem('access_token');
    if (!token) {
      this.isLoading = false;
      this.router.navigate(['/login']);
      return;
    }

    // Usamos el endpoint de gamificación que ahora tiene todos los datos del dashboard
    this.http.get<any>('http://localhost:8042/api/v1/gamification/dashboard/', {
      headers: { Authorization: `Bearer ${token}` }
    }).subscribe({
      next: (data) => {
        console.log('Dashboard data loaded:', data);
        // Mapeamos los datos para que el template siga funcionando
        this.userProfile = {
          ...data,
          // Recuperamos el nombre del localStorage si no viene en el dashboard
          first_name: localStorage.getItem('first_name') || 'Estudiante'
        };
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error loading dashboard:', err);
        this.isLoading = false;
        this.cdr.detectChanges();
        this.router.navigate(['/login']);
      }
    });
  }

  logout(event?: Event) {
    if (event) {
        event.preventDefault();
    }
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    this.router.navigate(['/login']);
  }
}

