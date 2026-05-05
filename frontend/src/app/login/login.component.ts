import { Component, inject, ChangeDetectorRef } from '@angular/core';
import { RouterLink, Router } from '@angular/router';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { NgIf } from '@angular/common';
import { AuthService } from '../shared/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [RouterLink, ReactiveFormsModule, NgIf],
  templateUrl: './login.component.html',
  styleUrl: './login.component.css'
})
export class LoginComponent {
  private fb = inject(FormBuilder);
  private authService = inject(AuthService);
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
    this.cdr.detectChanges();
    
    this.authService.login(this.loginForm.value).subscribe({
      next: () => {
        this.checkProfile();
      },
      error: () => {
        this.isLoading = false;
        // El error específico lo maneja el errorInterceptor mediante Toasts
        this.cdr.detectChanges();
      }
    });
  }

  checkProfile() {
    this.authService.loadUserProfile().subscribe({
      next: (profile) => {
        this.isLoading = false;
        this.cdr.detectChanges();
        
        if (profile.role === 'ROLE_ADMIN') {
          window.location.href = 'http://127.0.0.1:8000/admin/';
        } else {
          this.router.navigate(['/dashboard']);
        }
      },
      error: () => {
        this.isLoading = false;
        this.cdr.detectChanges();
      }
    });
  }
}
