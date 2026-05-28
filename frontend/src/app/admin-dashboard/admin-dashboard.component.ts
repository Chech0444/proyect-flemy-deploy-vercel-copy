import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { TopbarComponent } from '../shared/topbar/topbar.component';

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [CommonModule, TopbarComponent],
  templateUrl: './admin-dashboard.component.html',
  styleUrls: ['./admin-dashboard.component.css']
})
export class AdminDashboardComponent implements OnInit {
  private http = inject(HttpClient);
  
  stats: any = null;
  recentSales: any[] = [];
  isLoading = true;

  ngOnInit() {
    this.loadStats();
  }

  loadStats() {
    const token = localStorage.getItem('access_token');
    this.http.get<any>(`${environment.apiUrl}/gamification/admin-stats/`, {
      headers: { Authorization: `Bearer ${token}` }
    }).subscribe({
      next: (data) => {
        this.stats = data.stats;
        this.recentSales = data.recent_sales;
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }
}
