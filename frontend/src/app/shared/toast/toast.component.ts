import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NotificationService } from '../notification.service';

@Component({
  selector: 'app-toast',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="toast-container" *ngIf="currentToast">
      <div class="toast" [ngClass]="currentToast.type">
        <div class="toast-icon">
          <span class="material-icons">{{ getIcon(currentToast.type) }}</span>
        </div>
        <div class="toast-content">
          <p>{{ currentToast.message }}</p>
        </div>
        <button class="toast-close" (click)="close()">
          <span class="material-icons">close</span>
        </button>
        <div class="toast-progress"></div>
      </div>
    </div>
  `,
  styles: [`
    .toast-container {
      position: fixed;
      top: 2rem;
      right: 2rem;
      z-index: 9999;
      pointer-events: none;
    }

    .toast {
      pointer-events: auto;
      display: flex;
      align-items: center;
      min-width: 300px;
      max-width: 450px;
      background: rgba(18, 18, 22, 0.95);
      backdrop-filter: blur(12px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 12px;
      padding: 1rem;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
      animation: slideIn 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
      overflow: hidden;
      position: relative;
    }

    @keyframes slideIn {
      from { transform: translateX(120%); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }

    .toast.success { border-left: 4px solid #047857; }
    .toast.error { border-left: 4px solid #ef4444; }
    .toast.info { border-left: 4px solid #d4a853; }

    .toast-icon {
      margin-right: 1rem;
      display: flex;
      align-items: center;
    }

    .toast.success .toast-icon { color: #10b981; }
    .toast.error .toast-icon { color: #ef4444; }
    .toast.info .toast-icon { color: #d4a853; }

    .toast-content {
      flex: 1;
      color: #fff;
      font-size: 0.9rem;
      font-weight: 500;
    }

    .toast-content p {
      margin: 0;
    }

    .toast-close {
      background: transparent;
      border: none;
      color: rgba(255, 255, 255, 0.5);
      cursor: pointer;
      padding: 0.25rem;
      transition: color 0.2s;
    }

    .toast-close:hover {
      color: #fff;
    }

    .toast-progress {
      position: absolute;
      bottom: 0;
      left: 0;
      height: 3px;
      background: rgba(255, 255, 255, 0.2);
      width: 100%;
      animation: progress 5s linear forwards;
    }

    @keyframes progress {
      from { width: 100%; }
      to { width: 0%; }
    }
  `]
})
export class ToastComponent implements OnInit {
  private notificationService = inject(NotificationService);
  private cdr = inject(ChangeDetectorRef);
  currentToast: { type: string, message: string } | null = null;

  ngOnInit() {
    this.notificationService.uiNotifications$.subscribe(toast => {
      this.currentToast = toast;
      this.cdr.detectChanges();
    });
  }

  getIcon(type: string): string {
    switch (type) {
      case 'success': return 'check_circle';
      case 'error': return 'error';
      case 'info': return 'info';
      default: return 'notifications';
    }
  }

  close() {
    this.notificationService.clearUiNotification();
  }
}
