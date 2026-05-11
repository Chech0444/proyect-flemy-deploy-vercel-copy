import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, tap } from 'rxjs';
import { environment } from '../../environments/environment';

export interface Notification {
  id: number;
  type: string;
  title: string;
  message: string;
  is_read: boolean;
  action_url: string;
  created_at: string;
}

@Injectable({
  providedIn: 'root'
})
export class NotificationService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/auth/notifications`;

  private notificationsSubject = new BehaviorSubject<Notification[]>([]);
  public notifications$ = this.notificationsSubject.asObservable();

  private unreadCountSubject = new BehaviorSubject<number>(0);
  public unreadCount$ = this.unreadCountSubject.asObservable();

  // Local UI Notifications (Toasts)
  private uiNotificationsSubject = new BehaviorSubject<{type: string, message: string} | null>(null);
  public uiNotifications$ = this.uiNotificationsSubject.asObservable();

  private getAuthHeaders() {
    const token = localStorage.getItem('access_token');
    return { Authorization: `Bearer ${token}` };
  }

  showError(message: string) {
    this.uiNotificationsSubject.next({ type: 'error', message });
    setTimeout(() => this.clearUiNotification(), 5000);
  }

  showSuccess(message: string) {
    this.uiNotificationsSubject.next({ type: 'success', message });
    setTimeout(() => this.clearUiNotification(), 5000);
  }

  showInfo(message: string) {
    this.uiNotificationsSubject.next({ type: 'info', message });
    setTimeout(() => this.clearUiNotification(), 5000);
  }

  clearUiNotification() {
    this.uiNotificationsSubject.next(null);
  }

  loadNotifications() {
    this.http.get<Notification[]>(`${this.apiUrl}/`, {
      headers: this.getAuthHeaders()
    }).subscribe({
      next: (data) => {
        this.notificationsSubject.next(data);
        const unreadCount = data.filter(n => !n.is_read).length;
        this.unreadCountSubject.next(unreadCount);
      },
      error: (err) => console.error('Error loading notifications', err)
    });
  }

  markAsRead(id: number) {
    return this.http.patch(`${this.apiUrl}/${id}/read/`, {}, {
      headers: this.getAuthHeaders()
    }).pipe(
      tap(() => {
        const updated = this.notificationsSubject.value.map(n => 
          n.id === id ? { ...n, is_read: true } : n
        );
        this.notificationsSubject.next(updated);
        this.unreadCountSubject.next(updated.filter(n => !n.is_read).length);
      })
    );
  }

  markAllAsRead() {
    return this.http.patch(`${this.apiUrl}/read-all/`, {}, {
      headers: this.getAuthHeaders()
    }).pipe(
      tap(() => {
        const updated = this.notificationsSubject.value.map(n => ({ ...n, is_read: true }));
        this.notificationsSubject.next(updated);
        this.unreadCountSubject.next(0);
      })
    );
  }
}
