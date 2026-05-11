import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule, NgIf, NgFor } from '@angular/common';
import { RouterLink } from '@angular/router';
import { TopbarComponent } from '../shared/topbar/topbar.component';
import { AuthService } from '../shared/auth.service';
import { timeout, catchError, of } from 'rxjs';
import { environment } from '../../environments/environment';

@Component({
  selector: 'app-catalog',
  standalone: true,
  imports: [CommonModule, NgIf, NgFor, RouterLink, TopbarComponent],
  templateUrl: './catalog.component.html',
  styleUrls: ['./catalog.component.css']
})
export class CatalogComponent implements OnInit {
  private http = inject(HttpClient);
  private cdr = inject(ChangeDetectorRef);

  courses: any[] = [];
  isLoading = true;
  userProfile: any = null;
  isAdmin = false;
  private authService = inject(AuthService);

  ngOnInit() {
    this.isAdmin = this.authService.isAdmin();
    this.restoreProfileFromCache();
    this.loadCatalog();
    this.loadProfileDetails();
  }

  restoreProfileFromCache() {
    const username = localStorage.getItem('username');
    const firstName = localStorage.getItem('first_name');
    const role = localStorage.getItem('role');
    if (username || firstName) {
      this.userProfile = {
        username: username || 'Usuario',
        first_name: firstName || 'Estudiante',
        role: role || 'ROLE_FREE',
        photo: null
      };
      this.cdr.detectChanges();
    }
  }

  loadProfileDetails() {
    const token = localStorage.getItem('access_token');
    if (!token) return;
    this.http.get<any>(`${environment.apiUrl}/auth/profile/`, {
      headers: { Authorization: `Bearer ${token}` }
    }).pipe(
      timeout(5000),
      catchError(() => of(this.userProfile))
    ).subscribe({
      next: (data) => {
        if (data) {
          this.userProfile = data;
          if (data.username) localStorage.setItem('username', data.username);
          if (data.first_name) localStorage.setItem('first_name', data.first_name);
          this.cdr.detectChanges();
        }
      }
    });
  }

  loadCatalog() {
    this.isLoading = true;
    this.cdr.detectChanges();

    this.http.get<any[]>(`${environment.apiUrl}/courses/catalog/`)
      .pipe(
        timeout(10000),
        catchError(err => {
          console.error('Error:', err);
          return of(null);
        })
      )
      .subscribe({
        next: (data) => {
          if (data) {
            this.courses = data;
          } else {
            this.courses = [];
          }
          this.isLoading = false;
          this.cdr.detectChanges();
        },
        error: (err) => {
          console.error('Fallo total:', err);
          this.isLoading = false;
          this.cdr.detectChanges();
        }
      });
  }

  logout(event?: Event) {
    if (event) event.preventDefault();
    localStorage.clear();
    window.location.href = '/login';
  }
}
