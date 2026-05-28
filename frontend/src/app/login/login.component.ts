import { NgIf } from '@angular/common';
import { ChangeDetectorRef, Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../core/services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [RouterLink, ReactiveFormsModule, NgIf],
  templateUrl: './login.component.html',
  styleUrl: './login.component.css'
})
export class LoginComponent {
  private readonly fb = inject(FormBuilder);
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);
  private readonly cdr = inject(ChangeDetectorRef);

  readonly loginForm = this.fb.group({
    username: ['', Validators.required],
    password: ['', Validators.required]
  });

  isLoading = false;
  socialLoading: 'google' | 'github' | null = null;
  errorMessage = '';

  onSubmit(): void {
    if (this.loginForm.invalid) {
      this.loginForm.markAllAsTouched();
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';
    this.cdr.detectChanges();

    this.authService.login(this.loginForm.getRawValue()).subscribe({
      next: () => this.checkProfile(),
      error: (error) => {
        this.isLoading = false;
        this.errorMessage = this.getErrorMessage(error);
        this.cdr.detectChanges();
      }
    });
  }

  checkProfile(): void {
    this.authService.loadUserProfile().subscribe({
      next: (profile: any) => {
        this.isLoading = false;
        this.cdr.detectChanges();

        if (profile?.role === 'ROLE_ADMIN') {
          window.location.href = 'http://127.0.0.1:8000/admin/';
        } else {
          this.router.navigate(['/dashboard']);
        }
      },
      error: () => {
        this.isLoading = false;
        this.errorMessage = 'Tu sesion inicio, pero no pudimos cargar tu perfil.';
        this.cdr.detectChanges();
      }
    });
  }

  loginWithGoogle(): void {
    this.startSocialLogin('google');
  }

  loginWithGitHub(): void {
    this.startSocialLogin('github');
  }

  private startSocialLogin(provider: 'google' | 'github'): void {
    this.errorMessage = '';
    this.socialLoading = provider;

    try {
      if (provider === 'google') {
        this.authService.loginWithGoogle();
      } else {
        this.authService.loginWithGitHub();
      }
    } catch {
      this.socialLoading = null;
      this.errorMessage = `No pudimos redirigirte a ${provider === 'google' ? 'Google' : 'GitHub'}.`;
      this.cdr.detectChanges();
    }
  }

  private getErrorMessage(error: any): string {
    return error?.error?.detail
      || error?.error?.message
      || 'No pudimos iniciar sesion. Revisa tus credenciales e intenta de nuevo.';
  }
}
