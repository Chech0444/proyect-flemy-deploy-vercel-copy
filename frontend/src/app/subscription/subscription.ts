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
  isWompiLoading = false;
  isVerifyingPayment = false;
  showSimulatedForm = false;
  selectedPlan: 'MONTHLY' | 'YEARLY' = 'MONTHLY';
  showPaymentForm = false;
  userProfile: any = null;
  isAdmin = false;

  constructor() {
    this.paymentForm = this.fb.group({
      card_number: ['', [Validators.required, Validators.pattern(/^\d{16,19}|\d{4}(\s\d{4}){3}$/)]],
      card_holder: ['', [Validators.required]],
      expiry: ['', [Validators.required, Validators.pattern(/^(0[1-9]|1[0-2])\/\d{2}$/)]],
      cvv: ['', [Validators.required, Validators.pattern(/^\d{3}$/)]]
    });
  }

  ngOnInit() {
    this.isAdmin = this.authService.isAdmin();
    this.loadProfile();

    // Consultar parámetros para verificar si viene de regreso de Wompi
    this.route.queryParams.subscribe(params => {
      const transactionId = params['id'];
      if (transactionId) {
        this.verifyWompiTransaction(transactionId);
      }
    });
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
    this.showSimulatedForm = false; // Resetear para mostrar primero la selección de método
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

  payWithWompi(plan: 'MONTHLY' | 'YEARLY') {
    this.isWompiLoading = true;
    this.cdr.detectChanges();

    const token = localStorage.getItem('access_token');
    
    // Obtener configuración de Wompi desde el backend
    this.http.get<any>(`${environment.apiUrl}/billing/wompi/config/`, {
      headers: { Authorization: `Bearer ${token}` }
    }).subscribe({
      next: (config) => {
        const publicKey = config.public_key;
        
        // PSE solo soporta COP, así que convertimos el precio (ej. 19.99 USD a aprox 79.900 COP)
        const priceCop = plan === 'MONTHLY' ? 79900 : 799000;
        const amountInCents = priceCop * 100;
        
        // Generar una referencia única
        const userId = this.userProfile?.id || 'guest';
        const reference = `flemy_${userId}_${Date.now()}`;
        
        // URL a la que Wompi debe retornar al usuario tras el pago
        const redirectUrl = window.location.origin + '/subscription';
        
        // Construir URL de redirección segura a Wompi Webcheckout
        const wompiCheckoutUrl = `https://checkout.wompi.co/p/?public-key=${publicKey}&currency=COP&amount-in-cents=${amountInCents}&reference=${reference}&redirect-url=${redirectUrl}`;
        
        console.log('Redirigiendo a Wompi Checkout:', wompiCheckoutUrl);
        window.location.href = wompiCheckoutUrl;
      },
      error: (err) => {
        this.isWompiLoading = false;
        console.error('ERROR AL OBTENER CONFIG WOMPI:', err);
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
          this.notificationService.showSuccess('¡Suscripción Activada! Ahora eres miembro PREMIUM.');
          
          // Limpiar parámetros de la URL para evitar reprocesamientos si refrescan
          this.router.navigate([], {
            relativeTo: this.route,
            queryParams: { id: null },
            queryParamsHandling: 'merge'
          });

          // Recargar el perfil para actualizar en tiempo real el rol en toda la aplicación
          this.authService.loadUserProfile().subscribe();

          setTimeout(() => {
            this.router.navigate(['/dashboard']);
          }, 3000);
        } else if (res.status === 'PENDING') {
          this.notificationService.showInfo('Tu pago de PSE está pendiente de confirmación por el banco.');
          
          this.router.navigate([], {
            relativeTo: this.route,
            queryParams: { id: null },
            queryParamsHandling: 'merge'
          });

          setTimeout(() => {
            this.router.navigate(['/dashboard']);
          }, 3000);
        } else {
          this.notificationService.showError(res.detail || 'Tu transacción no fue aprobada por Wompi.');
          
          this.router.navigate([], {
            relativeTo: this.route,
            queryParams: { id: null },
            queryParamsHandling: 'merge'
          });
        }
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.isVerifyingPayment = false;
        console.error('ERROR EN VERIFICACIÓN:', err);
        const msg = err.error?.detail || 'No se pudo verificar el pago con Wompi.';
        this.notificationService.showError(msg);
        
        this.router.navigate([], {
          relativeTo: this.route,
          queryParams: { id: null },
          queryParamsHandling: 'merge'
        });
        
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

        // Recargar el perfil desde el servidor para actualizar el rol en toda la app
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
    localStorage.clear();
    this.router.navigate(['/login']);
  }
}
