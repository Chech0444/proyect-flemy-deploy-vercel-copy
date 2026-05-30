import { NgIf } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-auth-callback',
  standalone: true,
  imports: [NgIf, RouterLink],
  templateUrl: './callback.component.html',
  styleUrl: './callback.component.css'
})
export class CallbackComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly authService = inject(AuthService);

  isLoading = true;
  errorMessage = '';

  async ngOnInit(): Promise<void> {
    const params = this.route.snapshot.queryParamMap;
    const access = params.get('access');
    const refresh = params.get('refresh') ?? undefined;
    const error = params.get('error') || params.get('error_description');

    if (error) {
      this.showError(error);
      return;
    }

    if (!access) {
      this.showError('No se recibio el token de acceso desde el proveedor.');
      return;
    }

    try {
      await this.authService.handleAuthCallback(access, refresh);
    } catch (err) {
      this.showError(err instanceof Error ? err.message : 'No fue posible completar el inicio de sesion.');
    }
  }

  private showError(message: string): void {
    this.isLoading = false;
    this.errorMessage = message;
  }
}
