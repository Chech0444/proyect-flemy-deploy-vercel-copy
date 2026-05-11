import { Component, OnInit, ElementRef, HostListener, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { NotificationService, Notification } from '../notification.service';

@Component({
  selector: 'app-notifications',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './notifications.component.html',
  styleUrls: ['./notifications.component.css']
})
export class NotificationsComponent implements OnInit {
  private notificationService = inject(NotificationService);
  private router = inject(Router);
  private eRef = inject(ElementRef);

  notifications: Notification[] = [];
  unreadCount = 0;
  isOpen = false;

  ngOnInit() {
    this.notificationService.notifications$.subscribe(n => this.notifications = n);
    this.notificationService.unreadCount$.subscribe(c => this.unreadCount = c);
    this.notificationService.loadNotifications();
  }

  toggleDropdown() {
    this.isOpen = !this.isOpen;
    if (this.isOpen && this.unreadCount > 0) {
      // Optional: Mark all as read when opening? 
      // User requested a "mark as read" button originally, so we'll leave it manual
    }
  }

  @HostListener('document:click', ['$event'])
  clickout(event: Event) {
    if(!this.eRef.nativeElement.contains(event.target)) {
      this.isOpen = false;
    }
  }

  markAsRead(notification: Notification, event: Event) {
    event.stopPropagation();
    if (!notification.is_read) {
      this.notificationService.markAsRead(notification.id).subscribe();
    }
  }

  handleNotificationClick(notification: Notification) {
    if (!notification.is_read) {
        this.notificationService.markAsRead(notification.id).subscribe();
    }
    this.isOpen = false;
    if (notification.action_url) {
        this.router.navigate([notification.action_url]);
    }
  }

  markAllAsRead() {
    this.notificationService.markAllAsRead().subscribe();
  }

  getIconForType(type: string): string {
    switch(type) {
      case 'SUGGESTION': return 'neurology';
      case 'REMINDER': return 'schedule';
      case 'STREAK': return 'local_fire_department';
      default: return 'notifications';
    }
  }
}
