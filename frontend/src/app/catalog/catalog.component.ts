import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule, NgIf, NgFor } from '@angular/common';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { TopbarComponent } from '../shared/topbar/topbar.component';
import { AuthService } from '../shared/auth.service';
import { timeout, catchError, of } from 'rxjs';
import { environment } from '../../environments/environment';

@Component({
  selector: 'app-catalog',
  standalone: true,
  imports: [CommonModule, NgIf, NgFor, RouterLink, TopbarComponent, FormsModule],
  templateUrl: './catalog.component.html',
  styleUrls: ['./catalog.component.css']
})
export class CatalogComponent implements OnInit {
  private http = inject(HttpClient);
  private cdr = inject(ChangeDetectorRef);

  courses: any[] = [];
  suggestions: any[] = [];
  filteredCourses: any[] = [];
  isLoading = true;
  userProfile: any = null;
  isAdmin = false;
  brokenImages: Set<any> = new Set();
  private authService = inject(AuthService);

  searchQuery = '';
  selectedCategory = '';
  selectedLevel = '';
  selectedOrder = '-created_at';

  categories: string[] = [];
  levels: string[] = ['Básico', 'Intermedio', 'Avanzado'];

  ngOnInit() {
    this.isAdmin = this.authService.isAdmin();
    this.restoreProfileFromCache();
    this.loadCatalog();
    this.loadProfileDetails();
    this.loadSuggestions();
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
            this.extractCategories(data);
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

  loadSuggestions() {
    const token = localStorage.getItem('access_token');
    if (!token) return;
    this.http.get<any[]>(`${environment.apiUrl}/courses/suggestions/`, {
      headers: { Authorization: `Bearer ${token}` }
    }).pipe(timeout(5000), catchError(() => of([]))).subscribe({
      next: (data) => {
        this.suggestions = data || [];
        this.cdr.detectChanges();
      }
    });
  }

  extractCategories(courses: any[]) {
    const cats = new Set<string>();
    for (const c of courses) {
      if (c.category) cats.add(c.category);
    }
    this.categories = Array.from(cats).sort();
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

    if (this.selectedCategory) {
      result = result.filter(c => c.category === this.selectedCategory);
    }

    if (this.selectedLevel) {
      result = result.filter(c => c.level === this.selectedLevel);
    }

    if (this.selectedOrder === 'title') {
      result.sort((a, b) => a.title.localeCompare(b.title));
    } else if (this.selectedOrder === '-title') {
      result.sort((a, b) => b.title.localeCompare(a.title));
    } else if (this.selectedOrder === 'total_duration_minutes') {
      result.sort((a, b) => (a.total_duration_minutes || 0) - (b.total_duration_minutes || 0));
    } else if (this.selectedOrder === '-total_duration_minutes') {
      result.sort((a, b) => (b.total_duration_minutes || 0) - (a.total_duration_minutes || 0));
    } else if (this.selectedOrder === 'enrollment_count') {
      result.sort((a, b) => (a.enrollment_count || 0) - (b.enrollment_count || 0));
    } else if (this.selectedOrder === '-enrollment_count') {
      result.sort((a, b) => (b.enrollment_count || 0) - (a.enrollment_count || 0));
    } else if (this.selectedOrder === 'created_at') {
      result.sort((a, b) => new Date(a.created_at || 0).getTime() - new Date(b.created_at || 0).getTime());
    } else {
      result.sort((a, b) => new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime());
    }

    this.filteredCourses = result;
  }

  onSearchChange() {
    this.applyFilters();
  }

  onFilterChange() {
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
    localStorage.clear();
    window.location.href = '/login';
  }
}
