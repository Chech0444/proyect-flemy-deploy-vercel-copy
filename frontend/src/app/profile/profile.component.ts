import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { NgIf } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TopbarComponent } from '../shared/topbar/topbar.component';
import { SidebarComponent } from '../shared/sidebar/sidebar.component';
import { AuthService } from '../shared/auth.service';
import { NotificationService } from '../shared/notification.service';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [NgIf, FormsModule, TopbarComponent, SidebarComponent],
  templateUrl: './profile.component.html',
  styleUrl: './profile.component.css'
})
export class ProfileComponent implements OnInit {
  private authService = inject(AuthService);
  private notificationService = inject(NotificationService);
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

  showPasswordModal = false;
  oldPassword = '';
  newPassword = '';
  confirmPassword = '';
  isSavingPassword = false;
  passwordSuccess = false;
  passwordError = '';

  isDeletingAccount = false;
  isAdmin = false;

  ngOnInit() {
    this.isAdmin = this.authService.isAdmin();
    this.loadProfile();
  }

  loadProfile() {
    this.isLoading = true;
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
      last_name: this.userProfile.last_name,
      bio: this.userProfile.bio,
      preferences: this.userProfile.preferences
    };

    this.authService.updateProfile(updateData).subscribe({
      next: () => {
        this.isSaving = false;
        this.saveSuccess = true;
        if (this.userProfile.first_name) {
          sessionStorage.setItem('first_name', this.userProfile.first_name);
        }
        setTimeout(() => { this.saveSuccess = false; this.cdr.detectChanges(); }, 3000);
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error guardando perfil:', err);
        this.isSaving = false;
        this.notificationService.showError(err.error?.detail || 'Error al guardar el perfil.');
        this.cdr.detectChanges();
      }
    });
  }

  openPasswordModal() {
    this.showPasswordModal = true;
    this.oldPassword = '';
    this.newPassword = '';
    this.confirmPassword = '';
    this.passwordSuccess = false;
    this.passwordError = '';
  }

  closePasswordModal() {
    this.showPasswordModal = false;
    this.oldPassword = '';
    this.newPassword = '';
    this.confirmPassword = '';
    this.passwordError = '';
  }

  changePassword() {
    if (!this.oldPassword) {
      this.passwordError = 'Debes ingresar tu contrasena actual.';
      return;
    }
    if (this.newPassword !== this.confirmPassword) {
      this.passwordError = 'Las contrasenas no coinciden.';
      return;
    }
    if (this.newPassword.length < 8) {
      this.passwordError = 'La contrasena debe tener al menos 8 caracteres.';
      return;
    }

    this.isSavingPassword = true;
    this.passwordError = '';

    this.authService.changePassword(this.oldPassword, this.newPassword).subscribe({
      next: () => {
        this.isSavingPassword = false;
        this.passwordSuccess = true;
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.isSavingPassword = false;
        this.passwordError = err.error?.error || 'Error de conexion. Intente nuevamente.';
        this.cdr.detectChanges();
      }
    });
  }

  deleteAccount() {
    const confirmed = confirm(
      'Esta accion eliminara tu cuenta permanentemente y no se puede deshacer.'
    );
    if (!confirmed) return;

    this.isDeletingAccount = true;
    this.authService.deleteAccount().subscribe({
      next: () => {
      },
      error: (err) => {
        console.error('Error eliminando cuenta:', err);
        if (err.status === 405) {
          this.notificationService.showError('Funcion no disponible. Contacta al soporte.');
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
