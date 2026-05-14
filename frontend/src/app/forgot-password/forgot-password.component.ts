import { Component, inject, OnDestroy, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router, RouterLink } from '@angular/router';

import { environment } from '../../environments/environment';

@Component({
  selector: 'app-forgot-password',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './forgot-password.component.html',
  styleUrls: ['./forgot-password.component.css']
})
export class ForgotPasswordComponent implements OnDestroy {
  private http = inject(HttpClient);
  private router = inject(Router);
  private cdr = inject(ChangeDetectorRef);
  
  step: 1 | 2 = 1;
  email: string = '';
  code: string = '';
  newPassword: string = '';
  confirmPassword: string = '';
  
  isLoading = false;
  successMessage = '';
  errorMessage = '';

  timerInterval: any;
  timeLeft: number = 600; // 10 minutes

  ngOnDestroy() {
    this.clearTimer();
  }

  requestReset() {
    if (!this.email) return;

    this.isLoading = true;
    this.successMessage = '';
    this.errorMessage = '';

    const emailToReset = this.email.trim().toLowerCase();
    this.http.post(`${environment.apiUrl}/auth/password-reset/`, { email: emailToReset }).subscribe({
      next: (res: any) => {
        this.isLoading = false;
        this.step = 2;
        this.startTimer();
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.isLoading = false;
        this.errorMessage = err.error?.error || 'Ha ocurrido un error inesperado.';
        this.cdr.detectChanges();
      }
    });
  }

  confirmReset() {
    if (!this.code || !this.newPassword || !this.confirmPassword) {
      this.errorMessage = 'Completa todos los campos.';
      return;
    }

    if (this.newPassword !== this.confirmPassword) {
      this.errorMessage = 'Las contraseñas no coinciden.';
      return;
    }

    if (this.newPassword.length < 8) {
      this.errorMessage = 'La contraseña debe tener al menos 8 caracteres.';
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';
    this.successMessage = '';

    const payload = {
      email: this.email.trim().toLowerCase(),
      code: this.code.trim(),
      new_password: this.newPassword
    };

    this.http.post(`${environment.apiUrl}/auth/password-reset/confirm/`, payload).subscribe({
      next: (res: any) => {
        this.isLoading = false;
        this.successMessage = 'Contraseña actualizada exitosamente. Redirigiendo...';
        this.clearTimer();
        this.cdr.detectChanges();
        setTimeout(() => this.router.navigate(['/login']), 3000);
      },
      error: (err) => {
        this.isLoading = false;
        this.errorMessage = err.error?.error || 'Código inválido o expirado.';
        this.cdr.detectChanges();
      }
    });
  }

  startTimer() {
    this.clearTimer();
    this.timeLeft = 600;
    this.timerInterval = setInterval(() => {
      this.timeLeft--;
      if (this.timeLeft <= 0) {
        this.clearTimer();
        this.errorMessage = 'El tiempo ha expirado. Solicita un nuevo código.';
        this.step = 1;
        this.code = '';
        this.newPassword = '';
        this.confirmPassword = '';
      }
      this.cdr.detectChanges();
    }, 1000);
  }

  clearTimer() {
    if (this.timerInterval) {
      clearInterval(this.timerInterval);
    }
  }

  get formatTime(): string {
    const minutes = Math.floor(this.timeLeft / 60);
    const seconds = this.timeLeft % 60;
    return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
  }
}
