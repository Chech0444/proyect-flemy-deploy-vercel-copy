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
  products: any[] = [];
  showProductSection = false;
  isBuyingProduct = false;
  isProductWompiLoading = false;
  isVerifyingProductPurchase = false;
  selectedProduct: any = null;
  showProductSimulatedForm = false;
  showProductPaymentForm = false;
  productPurchaseForm: FormGroup;

  constructor() {
    this.paymentForm = this.fb.group({
      card_number: ['', [Validators.required, Validators.pattern(/^\d{16,19}|\d{4}(\s\d{4}){3}$/)]],
      card_holder: ['', [Validators.required]],
      expiry: ['', [Validators.required, Validators.pattern(/^(0[1-9]|1[0-2])\/\d{2}$/)]],
      cvv: ['', [Validators.required, Validators.pattern(/^\d{3}$/)]]
    });
    this.productPurchaseForm = this.fb.group({
      card_number: ['', [Validators.required, Validators.pattern(/^\d{16,19}|\d{4}(\s\d{4}){3}$/)]],
      card_holder: ['', [Validators.required]],
      expiry: ['', [Validators.required, Validators.pattern(/^(0[1-9]|1[0-2])\/\d{2}$/)]],
      cvv: ['', [Validators.required, Validators.pattern(/^\d{3}$/)]]
    });
  }

  ngOnInit() {
    this.isAdmin = this.authService.isAdmin();
    this.loadProfile();
    this.loadProducts();

    this.route.queryParams.subscribe(params => {
      const transactionId = params['id'];
      const purchaseTid = params['purchase_id'];
      if (purchaseTid) {
        const productId = params['product_id'];
        this.verifyWompiProductPurchase(purchaseTid, productId);
      } else if (transactionId) {
        this.verifyWompiTransaction(transactionId);
      }
    });
  }

  loadProducts() {
    const token = localStorage.getItem('access_token');
    if (!token) return;
    this.http.get<any[]>(`${environment.apiUrl}/billing/products/`, {
      headers: { Authorization: `Bearer ${token}` }
    }).subscribe({
      next: (data) => { this.products = data; this.cdr.detectChanges(); }
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
        const publicKey = config.public_key;
        const priceCop = plan === 'MONTHLY' ? 2000 : 799000;
        const amountInCents = priceCop * 100;
        const userId = this.userProfile?.id || 'guest';
        const reference = `flemy_${userId}_${Date.now()}`;
        const redirectUrl = window.location.origin + '/subscription';

        this.http.post<any>(`${environment.apiUrl}/billing/wompi/signature/`, {
          reference: reference,
          amount_in_cents: amountInCents,
          currency: 'COP'
        }, {
          headers: { Authorization: `Bearer ${token}` }
        }).subscribe({
          next: (sigRes) => {
            this.loadWompiScript().then(() => {
              this.isWompiLoading = false;
              this.cdr.detectChanges();

              const checkout = new (window as any).WidgetCheckout({
                currency: 'COP',
                amountInCents: amountInCents,
                reference: reference,
                publicKey: publicKey,
                redirectUrl: redirectUrl,
                signature: sigRes.signature
              });

              checkout.open((result: any) => {
                const transaction = result.transaction;
                if (transaction && transaction.id) {
                  this.verifyWompiTransaction(transaction.id);
                }
              });
            }).catch((err) => {
              this.isWompiLoading = false;
              console.error('ERROR:', err);
              this.notificationService.showError('No se pudo cargar la pasarela de pagos.');
              this.cdr.detectChanges();
            });
          },
          error: (err) => {
            this.isWompiLoading = false;
            console.error('ERROR AL OBTENER FIRMA:', err);
            this.notificationService.showError(err.error?.detail || 'Error de configuración de Wompi.');
            this.cdr.detectChanges();
          }
        });
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

  toggleProductSection() {
    this.showProductSection = !this.showProductSection;
    this.cdr.detectChanges();
  }

  buyProduct(product: any) {
    this.selectedProduct = product;
    this.showProductPaymentForm = true;
    this.showProductSimulatedForm = false;
    this.cdr.detectChanges();
  }

  goBackProduct() {
    if (this.showProductSimulatedForm) {
      this.showProductSimulatedForm = false;
    } else if (this.showProductPaymentForm) {
      this.showProductPaymentForm = false;
      this.selectedProduct = null;
    } else {
      this.showProductSection = false;
    }
    this.cdr.detectChanges();
  }

  buyProductWithWompi(product: any) {
    this.isProductWompiLoading = true;
    this.cdr.detectChanges();

    const token = localStorage.getItem('access_token');
    this.http.get<any>(`${environment.apiUrl}/billing/wompi/config/`, {
      headers: { Authorization: `Bearer ${token}` }
    }).subscribe({
      next: (config) => {
        const amountInCents = product.price_cop * 100;
        const userId = this.userProfile?.id || 'guest';
        const reference = `flemy_product_${product.id}_${userId}_${Date.now()}`;
        const redirectUrl = window.location.origin + '/subscription?purchase_id=REF&product_id=' + product.id;

        this.http.post<any>(`${environment.apiUrl}/billing/wompi/signature/`, {
          reference: reference,
          amount_in_cents: amountInCents,
          currency: 'COP'
        }, {
          headers: { Authorization: `Bearer ${token}` }
        }).subscribe({
          next: (sigRes) => {
            this.loadWompiScript().then(() => {
              this.isProductWompiLoading = false;
              this.cdr.detectChanges();

              const checkout = new (window as any).WidgetCheckout({
                currency: 'COP',
                amountInCents: amountInCents,
                reference: reference,
                publicKey: config.public_key,
                redirectUrl: redirectUrl.replace('REF', reference),
                signature: sigRes.signature
              });

              checkout.open((result: any) => {
                const transaction = result.transaction;
                if (transaction && transaction.id) {
                  this.verifyWompiProductPurchase(transaction.id, product.id);
                }
              });
            }).catch((err) => {
              this.isProductWompiLoading = false;
              console.error('ERROR:', err);
              this.notificationService.showError('No se pudo cargar la pasarela de pagos.');
              this.cdr.detectChanges();
            });
          },
          error: (err) => {
            this.isProductWompiLoading = false;
            console.error('ERROR AL OBTENER FIRMA:', err);
            this.notificationService.showError(err.error?.detail || 'Error de configuración de Wompi.');
            this.cdr.detectChanges();
          }
        });
      },
      error: (err) => {
        this.isProductWompiLoading = false;
        console.error('ERROR:', err);
        this.notificationService.showError('No se pudo iniciar el pago con Wompi.');
        this.cdr.detectChanges();
      }
    });
  }

  verifyWompiProductPurchase(transactionId: string, productId: string) {
    this.isVerifyingProductPurchase = true;
    this.cdr.detectChanges();

    const token = localStorage.getItem('access_token');
    this.http.post<any>(`${environment.apiUrl}/billing/wompi/purchase-verify/`, {
      transaction_id: transactionId,
      product_id: productId
    }, {
      headers: { Authorization: `Bearer ${token}` }
    }).subscribe({
      next: (res) => {
        this.isVerifyingProductPurchase = false;
        if (res.status === 'APPROVED') {
          this.notificationService.showSuccess(res.message);
          this.router.navigate([], {
            relativeTo: this.route,
            queryParams: { purchase_id: null, product_id: null },
            queryParamsHandling: 'merge'
          });
          this.selectedProduct = null;
          this.showProductPaymentForm = false;
        } else if (res.status === 'PENDING') {
          this.notificationService.showInfo('Pago pendiente de confirmación bancaria.');
          this.router.navigate([], {
            relativeTo: this.route,
            queryParams: { purchase_id: null, product_id: null },
            queryParamsHandling: 'merge'
          });
        } else {
          this.notificationService.showError(res.detail || 'Pago no aprobado.');
          this.router.navigate([], {
            relativeTo: this.route,
            queryParams: { purchase_id: null, product_id: null },
            queryParamsHandling: 'merge'
          });
        }
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.isVerifyingProductPurchase = false;
        console.error('ERROR:', err);
        this.notificationService.showError(err.error?.detail || 'No se pudo verificar el pago.');
        this.router.navigate([], {
          relativeTo: this.route,
          queryParams: { purchase_id: null, product_id: null },
          queryParamsHandling: 'merge'
        });
        this.cdr.detectChanges();
      }
    });
  }

  onSubmitProductPurchase() {
    if (this.productPurchaseForm.invalid) {
      this.notificationService.showError('Completa los datos de la tarjeta.');
      return;
    }
    this.isBuyingProduct = true;
    this.cdr.detectChanges();

    const payload = {
      ...this.productPurchaseForm.value,
      product_id: this.selectedProduct.id
    };

    const token = localStorage.getItem('access_token');
    this.http.post<any>(`${environment.apiUrl}/billing/purchase/simulate/`, payload, {
      headers: { Authorization: `Bearer ${token}` }
    }).subscribe({
      next: (res) => {
        this.isBuyingProduct = false;
        this.notificationService.showSuccess(res.message);
        this.selectedProduct = null;
        this.showProductPaymentForm = false;
        this.showProductSimulatedForm = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.isBuyingProduct = false;
        console.error('ERROR:', err);
        this.notificationService.showError(err.error?.detail || 'Error al procesar la compra.');
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
      this.productPurchaseForm.patchValue({ card_number: formatted }, { emitEvent: false });
    }
  }

  formatExpiry(event: any) {
    let value = event.target.value.replace(/\D/g, '');
    if (value.length >= 2) {
      value = value.substring(0, 2) + '/' + value.substring(2, 4);
    }
    this.paymentForm.patchValue({ expiry: value }, { emitEvent: false });
    this.productPurchaseForm.patchValue({ expiry: value }, { emitEvent: false });
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
