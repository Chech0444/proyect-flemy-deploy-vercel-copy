import { Component, inject } from '@angular/core';
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
export class ForgotPasswordComponent {
  private http = inject(HttpClient);
  
  email: string = '';
  isLoading = false;
  successMessage = '';
  errorMessage = '';

  onSubmit() {
    if (!this.email) return;

    this.isLoading = true;
    this.successMessage = '';
    this.errorMessage = '';

    this.http.post(`${environment.apiUrl}/auth/password-reset/`, { email: this.email }).subscribe({
      next: (res: any) => {
        this.isLoading = false;
        this.successMessage = res.message || 'Enlace enviado.';
      },
      error: (err) => {
        this.isLoading = false;
        // Even if email is wrong, django view returns 200 "Si tu correo etc".
        // But if 400 or network error:
        this.errorMessage = err.error?.error || 'Ha ocurrido un error inesperado al contactar al servidor.';
      }
    });
  }
}
