import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { RouterLink, Router } from '@angular/router';
import { NgIf, NgFor, NgClass, DatePipe, KeyValuePipe } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { TopbarComponent } from '../shared/topbar/topbar.component';
import { SkeletonComponent } from '../shared/skeleton/skeleton.component';
import { AuthService } from '../shared/auth.service';
import { environment } from '../../environments/environment';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [NgIf, NgFor, NgClass, DatePipe, KeyValuePipe, RouterLink, TopbarComponent, SkeletonComponent],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css'
})
export class DashboardComponent implements OnInit {
  private authService = inject(AuthService);
  private http = inject(HttpClient);
  private router = inject(Router);
  private cdr = inject(ChangeDetectorRef);
  private apiUrl = environment.apiUrl;

  userProfile: any = null;
  isAdmin = false;
  isLoading = true;

  ngOnInit() {
    this.loadProfile();
    this.isAdmin = this.authService.isAdmin();
  }

  get level(): number {
    return this.userProfile ? Math.floor(this.userProfile.xp / 100) + 1 : 1;
  }

  get xpInLevel(): number {
    return this.userProfile ? this.userProfile.xp % 100 : 0;
  }

  get xpProgressPercent(): number {
    return (this.xpInLevel / 100) * 100;
  }

  get nextLevelXp(): number {
    return 100 - this.xpInLevel;
  }

  get levelProgressLabel(): string {
    const base = this.level * 100;
    return `${base - 99}-${base} XP`;
  }

  timeAgo(dateStr: string): string {
    if (!dateStr) return '';
    const now = new Date();
    const date = new Date(dateStr.replace(' ', 'T'));
    const diffMs = now.getTime() - date.getTime();
    const diffMin = Math.floor(diffMs / 60000);
    if (diffMin < 1) return 'Ahora';
    if (diffMin < 60) return `hace ${diffMin}min`;
    const diffHrs = Math.floor(diffMin / 60);
    if (diffHrs < 24) return `hace ${diffHrs}h`;
    const diffDays = Math.floor(diffHrs / 24);
    if (diffDays === 1) return 'ayer';
    return `hace ${diffDays}días`;
  }

  loadProfile() {
    if (!this.authService.isLoggedIn()) {
      this.isLoading = false;
      this.router.navigate(['/login']);
      return;
    }

    this.http.get<any>(`${this.apiUrl}/gamification/dashboard/`).subscribe({
      next: (data) => {
        this.userProfile = {
          ...data,
          first_name: localStorage.getItem('first_name') || 'Estudiante'
        };
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error loading dashboard:', err);
        this.isLoading = false;
        this.cdr.detectChanges();
        if (err.status === 401) {
          this.authService.logout();
        }
      }
    });
  }

  logout(event?: Event) {
    if (event) event.preventDefault();
    this.authService.logout();
  }
}
