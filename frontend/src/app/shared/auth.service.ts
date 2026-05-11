import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { BehaviorSubject, Observable, tap, catchError, throwError } from 'rxjs';
import { environment } from '../../environments/environment';

export interface UserProfile {
  username: string;
  first_name: string;
  last_name: string;
  role: string;
  email: string;
  bio?: string;
  preferences?: any;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private http = inject(HttpClient);
  private router = inject(Router);
  private apiUrl = environment.apiUrl;

  private currentUserSubject = new BehaviorSubject<UserProfile | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  constructor() {
    const token = this.getToken();
    if (token) {
      this.loadUserProfile().subscribe();
    }
  }

  login(credentials: any): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/auth/login/`, credentials).pipe(
      tap(res => {
        if (res.access && res.refresh) {
          localStorage.setItem('access_token', res.access);
          localStorage.setItem('refresh_token', res.refresh);
          if (res.is_staff !== undefined) {
            localStorage.setItem('is_staff', res.is_staff ? 'true' : 'false');
          }
        }
      })
    );
  }

  logout() {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken && this.isLoggedIn()) {
        this.http.post(`${this.apiUrl}/auth/logout/`, { refresh: refreshToken })
          .subscribe({ error: () => {} });
      }
    } catch (e) {}

    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('username');
    localStorage.removeItem('first_name');
    localStorage.removeItem('role');
    localStorage.removeItem('is_staff');
    this.currentUserSubject.next(null);
    this.router.navigate(['/login']);
  }

  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  loadUserProfile(): Observable<UserProfile> {
    return this.http.get<UserProfile>(`${this.apiUrl}/auth/profile/`).pipe(
      tap(profile => {
        if (profile) {
          this.currentUserSubject.next(profile);
          localStorage.setItem('username', profile.username);
          localStorage.setItem('first_name', profile.first_name);
          localStorage.setItem('role', profile.role);
        }
      }),
      catchError(err => {
        if (err.status === 401) {
          this.logout();
        }
        return throwError(() => err);
      })
    );
  }

  updateProfile(profileData: any): Observable<UserProfile> {
    return this.http.patch<UserProfile>(`${this.apiUrl}/auth/profile/`, profileData).pipe(
      tap(profile => {
        this.currentUserSubject.next(profile);
        if (profile.first_name) localStorage.setItem('first_name', profile.first_name);
        if (profile.role) localStorage.setItem('role', profile.role);
      })
    );
  }

  changePassword(password: string): Observable<any> {
    return this.http.put(`${this.apiUrl}/auth/profile/change-password/`, { new_password: password });
  }

  deleteAccount(): Observable<any> {
    return this.http.delete(`${this.apiUrl}/auth/profile/delete-account/`).pipe(
      tap(() => this.logout())
    );
  }

  isLoggedIn(): boolean {
    const token = this.getToken();
    return !!token && token !== 'undefined';
  }

  isAdmin(): boolean {
    const role = this.currentUserValue?.role || localStorage.getItem('role');
    const isStaff = localStorage.getItem('is_staff') === 'true';
    return role === 'ROLE_ADMIN' || isStaff;
  }

  isPremium(): boolean {
    const role = this.currentUserValue?.role || localStorage.getItem('role');
    return role === 'ROLE_PREMIUM' || role === 'ROLE_ADMIN' || this.isAdmin();
  }

  get currentUserValue(): UserProfile | null {
    return this.currentUserSubject.value;
  }
}
