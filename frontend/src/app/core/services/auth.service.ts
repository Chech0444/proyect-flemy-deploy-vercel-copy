import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);

  private readonly apiUrl = `${environment.apiUrl}/auth`;
  private readonly backendUrl = new URL(environment.apiUrl).origin;
  private readonly callbackUrl = `${window.location.origin}/auth/callback`;
  private isAuthSubject = new BehaviorSubject<boolean>(this.hasToken());

  readonly isAuthenticated$ = this.isAuthSubject.asObservable();

  login(credentials: { username: string | null; password: string | null }): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/login/`, credentials).pipe(
      tap((response) => this.storeTokens(response.access, response.refresh))
    );
  }

  loadUserProfile(): Observable<any> {
    return this.http.get(`${this.apiUrl}/profile/`);
  }

  loginWithGoogle(): void {
    this.redirectToProvider('google');
  }

  loginWithGitHub(): void {
    this.redirectToProvider('github');
  }

  async handleAuthCallback(token: string, refresh?: string): Promise<boolean> {
    if (!token || token === 'undefined' || token === 'null') {
      throw new Error('No se recibio un token de acceso valido.');
    }

    this.storeTokens(token, refresh);
    return this.router.navigate(['/dashboard']);
  }

  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    this.isAuthSubject.next(false);
    this.router.navigate(['/login']);
  }

  private hasToken(): boolean {
    return !!localStorage.getItem('access_token');
  }

  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  private redirectToProvider(provider: 'google' | 'github'): void {
    const next = encodeURIComponent(this.callbackUrl);
    window.location.href = `${this.backendUrl}/accounts/${provider}/login/?process=login&next=${next}`;
  }

  private storeTokens(access?: string, refresh?: string): void {
    if (!access) {
      return;
    }

    localStorage.setItem('access_token', access);

    if (refresh) {
      localStorage.setItem('refresh_token', refresh);
    }

    this.isAuthSubject.next(true);
  }
}
