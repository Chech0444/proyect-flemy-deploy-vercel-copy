import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';

import { environment } from '../../environments/environment';

@Component({
  selector: 'app-reset-password',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './reset-password.component.html',
  styleUrls: ['../forgot-password/forgot-password.component.css'] // Reusando CSS para consistencia visual
})
export class ResetPasswordComponent implements OnInit {
  private http = inject(HttpClient);
  private route = inject(ActivatedRoute);
  private router = inject(Router);

  uidb64: string = '';
  token: string = '';
  newPassword = '';
  confirmPassword = '';
  
  isLoading = false;
  successMessage = '';
  errorMessage = '';

  ngOnInit() {
    this.uidb64 = this.route.snapshot.paramMap.get('uidb64') || '';
    this.token = this.route.snapshot.paramMap.get('token') || '';

    if (!this.uidb64 || !this.token) {
      this.errorMessage = 'El enlace es inválido o está corrupto.';
    }
  }

  onSubmit() {
    if (this.newPassword !== this.confirmPassword) {
      this.errorMessage = 'Las contraseñas no coinciden.';
      return;
    }
    
    if (this.newPassword.length < 8) {
      this.errorMessage = 'La contraseña debe tener mínimo 8 caracteres.';
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';
    this.successMessage = '';

    const payload = {
      uidb64: this.uidb64,
      token: this.token,
      new_password: this.newPassword
    };

    this.http.post(`${environment.apiUrl}/auth/password-reset/confirm/`, payload).subscribe({
      next: (res: any) => {
        this.isLoading = false;
        this.successMessage = '¡Contraseña actualizada exitosamente! Serás redirigido para iniciar sesión.';
        setTimeout(() => this.router.navigate(['/login']), 3000);
      },
      error: (err) => {
        this.isLoading = false;
        this.errorMessage = err.error?.error || 'Enlace expirado o inválido.';
      }
    });
  }
}
