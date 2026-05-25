import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { SocialAuthService, GoogleLoginProvider, SocialUser } from '@abacritt/angularx-social-login';
import { BehaviorSubject, tap } from 'rxjs';
import { Router } from '@angular/router';

@Injectable({ providedIn: 'root' })
export class AuthService {

  private apiUrl = 'http://127.0.0.1:8000/api/v1/auth';
  private isAuthSubject = new BehaviorSubject<boolean>(this.hasToken());
  isAuthenticated$ = this.isAuthSubject.asObservable();

  private http = inject(HttpClient);
  private socialAuth = inject(SocialAuthService);
  private router = inject(Router);

  // Login tradicional
  login(credentials: any) {
    return this.http.post(`${this.apiUrl}/login/`, credentials);
  }

  loadUserProfile() {
    return this.http.get(`${this.apiUrl}/user/`);
  }

  // ==================== SOCIAL LOGIN ====================
  loginWithGoogle() {
    this.socialAuth.signIn(GoogleLoginProvider.PROVIDER_ID).then((user: SocialUser) => {
      this.http.post(`${this.apiUrl}/social/google/`, {
        access_token: user.idToken
      }).pipe(
        tap((response: any) => {
          localStorage.setItem('access_token', response.access);
          if (response.refresh) localStorage.setItem('refresh_token', response.refresh);
          this.isAuthSubject.next(true);
          this.router.navigate(['/dashboard']);
        })
      ).subscribe();
    }).catch(err => console.error('Google Login Error:', err));
  }

  loginWithGitHub() {
    window.location.href = 'http://127.0.0.1:8000/accounts/github/login/';
  }

  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    this.socialAuth.signOut();
    this.isAuthSubject.next(false);
    this.router.navigate(['/login']);
  }

  private hasToken(): boolean {
    return !!localStorage.getItem('access_token');
  }

  getToken(): string | null {
    return localStorage.getItem('access_token');
  }
}