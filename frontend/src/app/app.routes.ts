import { Routes } from '@angular/router';
import { LoginComponent } from './login/login.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { Register } from './register/register';
import { ProgressComponent } from './progress/progress.component';
import { ProfileComponent } from './profile/profile.component';
import { CatalogComponent } from './catalog/catalog.component';

import { ForgotPasswordComponent } from './forgot-password/forgot-password.component';
import { SettingsComponent } from './settings/settings.component';
import { CourseDetailComponent } from './catalog/course-detail/course-detail.component';
import { SubscriptionComponent } from './subscription/subscription';
import { AdminDashboardComponent } from './admin-dashboard/admin-dashboard.component';
import { adminGuard } from './shared/admin.guard';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { path: 'register', component: Register },
  { path: 'forgot-password', component: ForgotPasswordComponent },
  { path: 'dashboard', component: DashboardComponent },
  { path: 'admin/dashboard', component: AdminDashboardComponent, canActivate: [adminGuard] },
  { path: 'progreso', component: ProgressComponent },
  { path: 'perfil', component: ProfileComponent },
  { path: 'configuracion', component: SettingsComponent },
  { path: 'catalog', component: CatalogComponent },
  { path: 'catalog/:slug', component: CourseDetailComponent },
  { path: 'subscription', component: SubscriptionComponent },
  { path: '', redirectTo: '/login', pathMatch: 'full' }
];
