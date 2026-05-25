import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { RouterLink, Router } from '@angular/router';
import { CommonModule } from '@angular/common';           // ← Agregado
import { HttpClient } from '@angular/common/http';
import { TopbarComponent } from '../shared/topbar/topbar.component';
import { SkeletonComponent } from '../shared/skeleton/skeleton.component';
import { AuthService } from '../shared/auth.service';
import { environment } from '../../environments/environment';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,           // ← Agregado (necesario para ngClass, ngIf, ngFor, etc.)
    RouterLink, 
    TopbarComponent, 
    SkeletonComponent
  ],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css'
})
export class DashboardComponent implements OnInit {
  private authService = inject(AuthService);
  private http = inject(HttpClient);
  private router = inject(Router);
  private cdr = inject(ChangeDetectorRef);
  private apiUrl = environment.apiUrl;

  userProfile: any = null;
  isAdmin = false;
  isLoading = true;

  ngOnInit() {
    this.loadProfile();
    this.isAdmin = this.authService.isAdmin?.() || false; // protección por si no existe el método
  }

  loadProfile() {
    if (!this.authService.isLoggedIn?.()) {
      this.isLoading = false;
      this.router.navigate(['/login']);
      return;
    }

    this.http.get<any>(`${this.apiUrl}/gamification/dashboard/`).subscribe({
      next: (data) => {
        this.userProfile = {
          ...data,
          first_name: localStorage.getItem('first_name') || 'Estudiante'
        };
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error loading dashboard:', err);
        this.isLoading = false;
        this.cdr.detectChanges();
        if (err.status === 401) {
          this.authService.logout();
        }
      }
    });
  }

  logout(event?: Event) {
    if (event) event.preventDefault();
    this.authService.logout();
  }
}

