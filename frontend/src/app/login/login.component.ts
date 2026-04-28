import { Component, inject, ChangeDetectorRef } from '@angular/core';
import { RouterLink, Router } from '@angular/router';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { NgIf } from '@angular/common';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [RouterLink, ReactiveFormsModule, NgIf],
  templateUrl: './login.component.html',
  styleUrl: './login.component.css'
})
export class LoginComponent {
  private fb = inject(FormBuilder);
  private http = inject(HttpClient);
  private router = inject(Router);
  private cdr = inject(ChangeDetectorRef);

  loginForm = this.fb.group({
    username: ['', Validators.required],
    password: ['', Validators.required]
  });

  isLoading = false;
  errorMessage = '';

  onSubmit() {
    if (this.loginForm.invalid) {
      this.loginForm.markAllAsTouched();
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';
    const { username, password } = this.loginForm.value;

    this.http.post<any>('http://localhost:8042/api/v1/auth/login/', { username, password }, { withCredentials: true })
      .subscribe({
        next: (res) => {
          localStorage.setItem('access_token', res.access);
          localStorage.setItem('refresh_token', res.refresh);
          this.checkProfile(res.access);
        },
        error: (err) => {
          this.isLoading = false;
          this.errorMessage = err.error?.detail || 'Credenciales inválidas';
          this.cdr.detectChanges();
        }
      });
  }

  checkProfile(token: string) {
    this.http.get<any>('http://localhost:8042/api/v1/auth/profile/', {
      headers: { Authorization: `Bearer ${token}` }
    }).subscribe({
      next: (profile) => {
        this.isLoading = false;
        this.cdr.detectChanges();
        if (profile.role === 'ROLE_ADMIN') {
          localStorage.setItem('first_name', profile.first_name);
          localStorage.setItem('username', profile.username);
          window.location.href = 'http://localhost:8042/admin/';
        } else {
          localStorage.setItem('first_name', profile.first_name);
          localStorage.setItem('username', profile.username);
          this.router.navigate(['/dashboard']);
        }
      },
      error: () => {
        this.isLoading = false;
        this.errorMessage = 'Error obteniendo el perfil';
        this.cdr.detectChanges();
      }
    });
  }
}
