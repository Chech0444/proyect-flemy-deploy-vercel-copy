import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { RouterLink, Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { NgIf, NgFor } from '@angular/common';
import { TopbarComponent } from '../shared/topbar/topbar.component';
import { SidebarComponent } from '../shared/sidebar/sidebar.component';
import { SkeletonComponent } from '../shared/skeleton/skeleton.component';
import { AuthService } from '../shared/auth.service';
import { environment } from '../../environments/environment';

@Component({
  selector: 'app-progress',
  standalone: true,
  imports: [NgIf, NgFor, RouterLink, TopbarComponent, SidebarComponent, SkeletonComponent],
  templateUrl: './progress.component.html',
  styleUrl: './progress.component.css'
})
export class ProgressComponent implements OnInit {
  private http = inject(HttpClient);
  private router = inject(Router);
  private cdr = inject(ChangeDetectorRef);

  progressData: any = null;
  leaderboardData: any[] = [];
  isLoading = true;
  hasError = false;
  userProfile: any = null;
  isAdmin = false;
  brokenImages: Set<string> = new Set();
  heatmapWeeks: { date: string; value: number; day: number }[][] = [];
  private authService = inject(AuthService);

  ngOnInit() {
    this.isAdmin = this.authService.isAdmin();
    this.loadProfile();
    this.loadProgress();
    this.loadLeaderboard();
  }

  loadProfile() {
    this.userProfile = {
      first_name: localStorage.getItem('first_name') || 'Estudiante',
      username: localStorage.getItem('username') || 'Usuario',
      role: localStorage.getItem('role') || 'ROLE_FREE'
    };
  }

  loadProgress() {
    if (!this.authService.isLoggedIn()) {
      this.isLoading = false;
      this.hasError = true;
      return;
    }

    this.isLoading = true;
    this.hasError = false;

    this.http.get<any>(`${environment.apiUrl}/gamification/progress/`).subscribe({
      next: (data) => {
        this.progressData = data;
        this.buildHeatmap(data.heatmap_data);
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error loading progress:', err);
        this.isLoading = false;
        this.hasError = true;
        this.cdr.detectChanges();
      }
    });
  }

  loadLeaderboard() {
    if (!this.authService.isLoggedIn()) return;
    this.http.get<any[]>(`${environment.apiUrl}/gamification/leaderboard/`).subscribe({
      next: (data) => {
        this.leaderboardData = data.slice(0, 5);
        this.cdr.detectChanges();
      },
      error: () => {}
    });
  }

  buildHeatmap(heatmapData: Record<string, number>) {
    if (!heatmapData) return;
    const sorted = Object.entries(heatmapData).sort(([a], [b]) => a.localeCompare(b));
    const weeks: { date: string; value: number; day: number }[][] = [];
    let currentWeek: { date: string; value: number; day: number }[] = [];
    let firstDate = new Date(sorted[0][0]);
    let firstDay = firstDate.getDay();
    let pad = firstDay === 0 ? 6 : firstDay - 1;
    for (let i = 0; i < pad; i++) {
      currentWeek.push({ date: '', value: -1, day: i });
    }
    for (const [date, value] of sorted) {
      const d = new Date(date);
      let day = d.getDay();
      if (day === 0) day = 7;
      currentWeek.push({ date, value, day: day - 1 });
      if (currentWeek.length === 7) {
        weeks.push(currentWeek);
        currentWeek = [];
      }
    }
    if (currentWeek.length > 0) {
      while (currentWeek.length < 7) {
        currentWeek.push({ date: '', value: -1, day: currentWeek.length });
      }
      weeks.push(currentWeek);
    }
    this.heatmapWeeks = weeks;
  }

  get level(): number {
    return this.progressData?.level || 1;
  }

  get xpInLevel(): number {
    return this.progressData?.xp_progress || 0;
  }

  get xpProgressPercent(): number {
    return this.xpInLevel;
  }

  get nextLevelXp(): number {
    return 100 - this.xpInLevel;
  }

  get completedCourses(): number {
    if (!this.progressData?.course_breakdown) return 0;
    return this.progressData.course_breakdown.filter((c: any) => c.progress >= 100).length;
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

  onImageError(key: string) {
    this.brokenImages.add(key);
    this.cdr.detectChanges();
  }

  isImageBroken(key: string): boolean {
    return this.brokenImages.has(key);
  }

  getMediaUrl(path: string | null | undefined): string | null {
    if (!path) return null;
    if (path.startsWith('http')) return path;
    return `${environment.apiUrl.replace('/api/v1', '')}${path}`;
  }

  getCertificateDownloadUrl(code: string): string {
    return `${environment.apiUrl}/certificates/${code}/download/`;
  }

  isCurrentUser(username: string): boolean {
    return this.progressData?.username === username;
  }

  logout(event?: Event) {
    if (event) event.preventDefault();
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    this.router.navigate(['/login']);
  }
}
