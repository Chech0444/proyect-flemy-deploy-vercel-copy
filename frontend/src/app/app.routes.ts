import { Routes } from '@angular/router';
import { LoginComponent } from './login/login.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { Register } from './register/register';
import { ProgressComponent } from './progress/progress.component';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { path: 'register', component: Register },
  { path: 'dashboard', component: DashboardComponent },
  { path: 'progreso', component: ProgressComponent },
  { path: '', redirectTo: '/login', pathMatch: 'full' }
];
