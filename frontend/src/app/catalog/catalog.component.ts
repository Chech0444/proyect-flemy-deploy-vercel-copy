import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule, NgIf, NgFor } from '@angular/common';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { TopbarComponent } from '../shared/topbar/topbar.component';
import { SidebarComponent } from '../shared/sidebar/sidebar.component';
import { AuthService } from '../shared/auth.service';
import { timeout, catchError, of } from 'rxjs';
import { environment } from '../../environments/environment';

@Component({
  selector: 'app-catalog',
  standalone: true,
  imports: [CommonModule, NgIf, NgFor, RouterLink, TopbarComponent, SidebarComponent, FormsModule],
  templateUrl: './catalog.component.html',
  styleUrls: ['./catalog.component.css']
})
export class CatalogComponent implements OnInit {
  private http = inject(HttpClient);
  private cdr = inject(ChangeDetectorRef);

  courses: any[] = [];
  filteredCourses: any[] = [];
  isLoading = true;
  userProfile: any = null;
  isAdmin = false;
  brokenImages: Set<any> = new Set();
  private authService = inject(AuthService);

  searchQuery = '';
  selectedLevel = '';

  levels: string[] = ['Básico', 'Intermedio', 'Avanzado'];

  ngOnInit() {
    this.isAdmin = this.authService.isAdmin();
    this.restoreProfileFromCache();
    this.loadCatalog();
    this.loadProfileDetails();
  }

  restoreProfileFromCache() {
    const username = sessionStorage.getItem('username');
    const firstName = sessionStorage.getItem('first_name');
    const role = sessionStorage.getItem('role');
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
    if (!this.authService.isLoggedIn()) return;
    this.http.get<any>(`${environment.apiUrl}/auth/profile/`).pipe(
      timeout(5000),
      catchError(() => of(this.userProfile))
    ).subscribe({
      next: (data) => {
        if (data) {
          this.userProfile = data;
          if (data.username) sessionStorage.setItem('username', data.username);
          if (data.first_name) sessionStorage.setItem('first_name', data.first_name);
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
            this.applyFilters();
          } else {
            this.courses = [];
            this.filteredCourses = [];
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

  toggleLevel(level: string) {
    this.selectedLevel = this.selectedLevel === level ? '' : level;
    this.applyFilters();
  }

  applyFilters() {
    let result = [...this.courses];

    if (this.searchQuery.trim()) {
      const q = this.searchQuery.toLowerCase();
      result = result.filter(c =>
        c.title.toLowerCase().includes(q) ||
        (c.short_description || '').toLowerCase().includes(q)
      );
    }

    if (this.selectedLevel) {
      result = result.filter(c => c.level === this.selectedLevel);
    }

    this.filteredCourses = result;
  }

  onSearchChange() {
    this.applyFilters();
  }

  onImageError(course: any) {
    this.brokenImages.add(course);
    this.cdr.detectChanges();
  }

  isImageBroken(course: any): boolean {
    return this.brokenImages.has(course);
  }

  logout(event?: Event) {
    if (event) event.preventDefault();
    sessionStorage.clear();
    window.location.href = '/login';
  }
}
