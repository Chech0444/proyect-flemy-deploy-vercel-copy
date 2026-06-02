import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router, RouterLink, ActivatedRoute } from '@angular/router';
import { environment } from '../../environments/environment';
import { NotificationService } from '../shared/notification.service';
import { TopbarComponent } from '../shared/topbar/topbar.component';
import { AuthService } from '../shared/auth.service';


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
  private route = inject(ActivatedRoute);
  private authService = inject(AuthService);

  paymentForm: FormGroup;
  isLoading = false;
  isLoadingPage = true;
  isWompiLoading = false;
  isVerifyingPayment = false;
  showSimulatedForm = false;
  selectedPlan: 'MONTHLY' | 'YEARLY' = 'MONTHLY';
  showPaymentForm = false;
  userProfile: any = null;
  isAdmin = false;
  isPremium = false;

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

    this.route.queryParams.subscribe(params => {
      const transactionId = params['id'];
      const plan = params['plan'];
      if (plan === 'MONTHLY' || plan === 'YEARLY') {
        this.selectedPlan = plan;
      }
      if (transactionId) {
        this.verifyWompiTransaction(transactionId);
      }
    });
  }

  loadProfile() {
    this.isLoadingPage = true;
    const token = localStorage.getItem('access_token');
    if (!token) {
      this.isLoadingPage = false;
      return;
    }
    this.http.get<any>(`${environment.apiUrl}/auth/profile/`, {
      headers: { Authorization: `Bearer ${token}` }
    }).subscribe({
      next: (data) => {
        this.userProfile = data;
        this.isAdmin = this.authService.isAdmin();
        this.isPremium = this.authService.isPremium();
        this.isLoadingPage = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.isLoadingPage = false;
        this.cdr.detectChanges();
      }
    });
  }

  selectPlan(plan: 'MONTHLY' | 'YEARLY') {
    this.selectedPlan = plan;
    this.showPaymentForm = true;
    this.showSimulatedForm = false;
    this.cdr.detectChanges();
  }

  setPlanToggle(plan: 'MONTHLY' | 'YEARLY') {
    this.selectedPlan = plan;
    this.cdr.detectChanges();
  }

  goBack() {
    if (this.showSimulatedForm) {
      this.showSimulatedForm = false;
    } else {
      this.showPaymentForm = false;
    }
    this.cdr.detectChanges();
  }

  loadWompiScript(): Promise<void> {
    return new Promise((resolve, reject) => {
      if ((window as any).WidgetCheckout) {
        resolve();
        return;
      }
      const script = document.createElement('script');
      script.src = 'https://checkout.wompi.co/widget.js';
      script.type = 'text/javascript';
      script.async = true;
      script.onload = () => resolve();
      script.onerror = () => reject(new Error('Failed to load Wompi script'));
      document.body.appendChild(script);
    });
  }

  payWithWompi(plan: 'MONTHLY' | 'YEARLY') {
    this.isWompiLoading = true;
    this.cdr.detectChanges();

    const token = localStorage.getItem('access_token');

    this.http.get<any>(`${environment.apiUrl}/billing/wompi/config/`, {
      headers: { Authorization: `Bearer ${token}` }
    }).subscribe({
      next: (config) => {
        const priceCop = plan === 'MONTHLY' ? 79900 : 799000;
        const amountInCents = priceCop * 100;
        const userId = this.userProfile?.id || 'guest';
        const reference = `flemy_${userId}_${Date.now()}`;
        const redirectUrl = window.location.origin + '/subscription?id=REF&plan=' + plan;

        this.http.post<any>(`${environment.apiUrl}/billing/wompi/signature/`, {
          reference, amount_in_cents: amountInCents, currency: 'COP'
        }, { headers: { Authorization: `Bearer ${token}` } }).subscribe({
          next: (sig) => {
            this.loadWompiScript().then(() => {
              this.isWompiLoading = false;
              this.cdr.detectChanges();

              const checkout = new (window as any).WidgetCheckout({
                currency: 'COP',
                amountInCents,
                reference,
                publicKey: config.public_key,
                redirectUrl: redirectUrl.replace('REF', reference),
                'signature:integrity': sig.signature
              });

              checkout.open((result: any) => {
                const transaction = result.transaction;
                if (transaction && transaction.id) {
                  this.verifyWompiTransaction(transaction.id);
                }
              });
            }).catch(() => {
              this.isWompiLoading = false;
              this.notificationService.showError('No se pudo cargar la pasarela de pagos.');
              this.cdr.detectChanges();
            });
          },
          error: (err) => {
            this.isWompiLoading = false;
            this.notificationService.showError(err.error?.detail || 'Error de firma Wompi.');
            this.cdr.detectChanges();
          }
        });
      },
      error: () => {
        this.isWompiLoading = false;
        this.notificationService.showError('No se pudo iniciar el proceso de pago con Wompi.');
        this.cdr.detectChanges();
      }
    });
  }

  verifyWompiTransaction(transactionId: string) {
    this.isVerifyingPayment = true;
    this.cdr.detectChanges();

    const token = localStorage.getItem('access_token');
    const payload = {
      transaction_id: transactionId,
      plan: this.selectedPlan
    };

    this.http.post<any>(`${environment.apiUrl}/billing/wompi/verify/`, payload, {
      headers: { Authorization: `Bearer ${token}` }
    }).subscribe({
      next: (res) => {
        this.isVerifyingPayment = false;

        if (res.status === 'APPROVED') {
          const planLabel = this.selectedPlan === 'YEARLY' ? 'ANUAL' : 'PREMIUM';
          this.notificationService.showSuccess(`Suscripción Activada! Ahora eres miembro ${planLabel}.`);

          this.router.navigate([], {
            relativeTo: this.route,
            queryParams: { id: null, plan: null },
            queryParamsHandling: 'merge'
          });

          this.authService.loadUserProfile().subscribe();

          setTimeout(() => {
            this.router.navigate(['/dashboard']);
          }, 3000);
        } else if (res.status === 'PENDING') {
          this.notificationService.showInfo('Tu pago de PSE está pendiente de confirmación por el banco.');

          this.router.navigate([], {
            relativeTo: this.route,
            queryParams: { id: null, plan: null },
            queryParamsHandling: 'merge'
          });

          setTimeout(() => {
            this.router.navigate(['/dashboard']);
          }, 3000);
        } else {
          this.notificationService.showError(res.detail || 'Tu transacción no fue aprobada por Wompi.');

          this.router.navigate([], {
            relativeTo: this.route,
            queryParams: { id: null, plan: null },
            queryParamsHandling: 'merge'
          });
        }
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.isVerifyingPayment = false;
        console.error('ERROR EN VERIFICACIÓN:', err);
        const msg = err.error?.detail || 'No se pudo verificar el pago con Wompi.';

        this.router.navigate([], {
          relativeTo: this.route,
          queryParams: { id: null, plan: null },
          queryParamsHandling: 'merge'
        });

        this.notificationService.showError(msg);
        this.cdr.detectChanges();
      }
    });
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
      const formatted = parts.join(' ');
      this.paymentForm.patchValue({ card_number: formatted }, { emitEvent: false });
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
        this.notificationService.showSuccess('Suscripción Activada! Ahora eres miembro PREMIUM.');

        this.authService.loadUserProfile().subscribe();

        setTimeout(() => {
          this.router.navigate(['/dashboard']);
        }, 2000);
      },
      error: (err) => {
        this.isLoading = false;
        console.error('ERROR EN PAGO:', err);
        const msg = err.error?.detail || 'No pudimos procesar tu pago. Revisa los datos.';
        this.notificationService.showError(msg);
        this.cdr.detectChanges();
      }
    });
  }

  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('username');
    localStorage.removeItem('first_name');
    localStorage.removeItem('role');
    this.router.navigate(['/login']);
  }
}
