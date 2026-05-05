import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { RouterLink, Router } from '@angular/router';
import { NgIf } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TopbarComponent } from '../shared/topbar/topbar.component';
import { AuthService } from '../shared/auth.service';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [NgIf, RouterLink, FormsModule, TopbarComponent],
  templateUrl: './profile.component.html',
  styleUrl: './profile.component.css'
})
export class ProfileComponent implements OnInit {
  private authService = inject(AuthService);
  private router = inject(Router);
  private cdr = inject(ChangeDetectorRef);

  userProfile: any = {
    first_name: '',
    last_name: '',
    username: '',
    email: '',
    bio: '',
    role: 'ROLE_FREE',
    xp: 0,
    study_streak: 0,
    preferences: {
      difficulty: 'intermedio',
      language: 'es'
    }
  };

  isLoading = true;
  isSaving = false;
  saveSuccess = false;

  // Modal cambio de contraseña
  showPasswordModal = false;
  newPassword = '';
  confirmPassword = '';
  isSavingPassword = false;
  passwordSuccess = false;
  passwordError = '';

  // Eliminar cuenta
  isDeletingAccount = false;

  ngOnInit() {
    this.loadProfile();
  }

  loadProfile() {
    this.authService.loadUserProfile().subscribe({
      next: (data) => {
        this.userProfile = {
          ...data,
          preferences: data.preferences && Object.keys(data.preferences).length > 0
            ? data.preferences
            : { difficulty: 'intermedio', language: 'es' }
        };
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error cargando perfil:', err);
        this.isLoading = false;
        this.cdr.detectChanges();
      }
    });
  }

  saveProfile() {
    this.isSaving = true;
    const updateData = {
      first_name: this.userProfile.first_name,
      last_name:  this.userProfile.last_name,
      bio:        this.userProfile.bio,
      preferences: this.userProfile.preferences
    };

    this.authService.updateProfile(updateData).subscribe({
      next: () => {
        this.isSaving = false;
        this.saveSuccess = true;
        setTimeout(() => { this.saveSuccess = false; this.cdr.detectChanges(); }, 3000);
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error guardando perfil:', err);
        this.isSaving = false;
        this.cdr.detectChanges();
      }
    });
  }

  openPasswordModal() {
    this.showPasswordModal = true;
    this.newPassword = '';
    this.confirmPassword = '';
    this.passwordSuccess = false;
    this.passwordError = '';
  }

  closePasswordModal() {
    this.showPasswordModal = false;
    this.newPassword = '';
    this.confirmPassword = '';
    this.passwordError = '';
  }

  changePassword() {
    if (this.newPassword !== this.confirmPassword) {
      this.passwordError = 'Las contraseñas no coinciden.';
      return;
    }
    if (this.newPassword.length < 8) {
      this.passwordError = 'La contraseña debe tener al menos 8 caracteres.';
      return;
    }

    this.isSavingPassword = true;
    this.passwordError = '';
    
    this.authService.changePassword(this.newPassword).subscribe({
      next: () => {
        this.isSavingPassword = false;
        this.passwordSuccess = true;
      },
      error: (err) => {
        this.isSavingPassword = false;
        this.passwordError = err.error?.error || 'Error de conexión. Intente nuevamente.';
      }
    });
  }

  deleteAccount() {
    const confirmed = confirm(
      '⚠️ ¿Estás completamente seguro?\n\nEsta acción eliminará tu cuenta permanentemente y no se puede deshacer.'
    );
    if (!confirmed) return;

    this.isDeletingAccount = true;
    this.authService.deleteAccount().subscribe({
      next: () => {
        // AuthService.logout handles clearing and navigation
      },
      error: (err) => {
        console.error('Error eliminando cuenta:', err);
        if (err.status === 405) {
          alert('Función no disponible en este momento. Contacta al soporte.');
        }
        this.isDeletingAccount = false;
        this.cdr.detectChanges();
      }
    });
  }

  logout(event?: Event) {
    if (event) event.preventDefault();
    this.authService.logout();
  }
}
