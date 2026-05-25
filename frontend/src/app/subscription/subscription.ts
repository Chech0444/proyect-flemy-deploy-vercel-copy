import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router, RouterLink } from '@angular/router';
import { environment } from '../../environments/environment';
import { NotificationService } from '../shared/notification.service';
import { TopbarComponent } from '../shared/topbar/topbar.component';
import { AuthService } from '../core/services/auth.service';

@Component({
  selector: 'app-subscription',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule, RouterLink, TopbarComponent],
  templateUrl: './subscription.html',
  styleUrls: ['./subscription.css']
})
export class SubscriptionComponent implements OnInit {
  
  private http = inject(HttpClient);
  private fb = inject(FormBuilder);
  private notificationService = inject(NotificationService);
  private cdr = inject(ChangeDetectorRef);
  private router = inject(Router);
  private authService = inject(AuthService);

  paymentForm: FormGroup;
  isLoading = false;
  selectedPlan: 'MONTHLY' | 'YEARLY' = 'MONTHLY';
  showPaymentForm = false;
  userProfile: any = null;

  constructor() {
    this.paymentForm = this.fb.group({
      card_number: ['', [Validators.required, Validators.pattern(/^\d{16,19}|\d{4}(\s\d{4}){3}$/)]],
      card_holder: ['', [Validators.required]],
      expiry: ['', [Validators.required, Validators.pattern(/^(0[1-9]|1[0-2])\/\d{2}$/)]],
      cvv: ['', [Validators.required, Validators.pattern(/^\d{3}$/)]]
    });
  }

  ngOnInit() {
    this.loadProfile();
  }

  loadProfile() {
    const token = localStorage.getItem('access_token');
    if (!token) return;
    this.http.get<any>(`${environment.apiUrl}/auth/profile/`, {
      headers: { Authorization: `Bearer ${token}` }
    }).subscribe({
      next: (data) => {
        this.userProfile = data;
        this.cdr.detectChanges();
      }
    });
  }

  selectPlan(plan: 'MONTHLY' | 'YEARLY') {
    this.selectedPlan = plan;
    this.showPaymentForm = true;
    this.cdr.detectChanges();
  }

  formatCardNumber(event: any) {
    let value = event.target.value.replace(/\s+/g, '').replace(/[^0-9]/gi, '');
    let matches = value.match(/\d{4,16}/g);
    let match = (matches && matches[0]) || '';
    let parts = [];

    for (let i = 0, len = match.length; i < len; i += 4) {
      parts.push(match.substring(i, i + 4));
    }

    if (parts.length) {
      this.paymentForm.patchValue({ card_number: parts.join(' ') }, { emitEvent: false });
    }
  }

  formatExpiry(event: any) {
    let value = event.target.value.replace(/\D/g, '');
    if (value.length >= 2) {
      value = value.substring(0, 2) + '/' + value.substring(2, 4);
    }
    this.paymentForm.patchValue({ expiry: value }, { emitEvent: false });
  }

  onSubmit() {
    if (this.paymentForm.invalid) {
      this.notificationService.showError('Por favor, completa los datos de la tarjeta correctamente.');
      return;
    }

    this.isLoading = true;
    this.cdr.detectChanges();

    const payload = {
      ...this.paymentForm.value,
      plan: this.selectedPlan
    };

    const token = localStorage.getItem('access_token');
    this.http.post<any>(`${environment.apiUrl}/billing/pay/simulate/`, payload, {
      headers: { Authorization: `Bearer ${token}` }
    }).subscribe({
      next: (res) => {
        this.isLoading = false;
        this.notificationService.showSuccess('¡Suscripción Activada! Ahora eres miembro PREMIUM.');
        
        this.authService.loadUserProfile().subscribe();
        
        setTimeout(() => {
          this.router.navigate(['/dashboard']);
        }, 2000);
      },
      error: (err) => {
        this.isLoading = false;
        console.error('ERROR EN PAGO:', err);
        const msg = err.error?.detail || 'No pudimos procesar tu pago.';
        this.notificationService.showError(msg);
        this.cdr.detectChanges();
      }
    });
  }

  logout() {
    localStorage.clear();
    this.router.navigate(['/login']);
  }
}