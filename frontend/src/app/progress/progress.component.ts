import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { RouterLink, Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { NgIf, NgFor, KeyValuePipe } from '@angular/common';

@Component({
  selector: 'app-progress',
  standalone: true,
  imports: [NgIf, NgFor, RouterLink, KeyValuePipe],
  templateUrl: './progress.component.html',
  styleUrl: './progress.component.css'
})
export class ProgressComponent implements OnInit {
  private http = inject(HttpClient);
  private router = inject(Router);
  private cdr = inject(ChangeDetectorRef);

  progressData: any = null;
  isLoading = true;
  userProfile: any = null;

  ngOnInit() {
    this.loadProgress();
    this.loadProfile();
  }

  loadProfile() {
    this.userProfile = {
      first_name: localStorage.getItem('first_name') || 'Estudiante',
      username: localStorage.getItem('username') || 'Usuario'
    };
  }

  loadProgress() {
    const token = localStorage.getItem('access_token');
    if (!token) {
      this.isLoading = false;
      this.router.navigate(['/login']);
      return;
    }

    this.http.get<any>('http://localhost:8042/api/v1/gamification/progress/', {
      headers: { Authorization: `Bearer ${token}` }
    }).subscribe({
      next: (data) => {
        console.log('Progress data loaded:', data);
        this.progressData = data;
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error loading progress:', err);
        this.isLoading = false;
        this.cdr.detectChanges();
        this.router.navigate(['/login']);
      }
    });
  }

  logout(event?: Event) {
    if (event) event.preventDefault();
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    this.router.navigate(['/login']);
  }
}
