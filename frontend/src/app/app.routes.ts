import { Routes } from '@angular/router';

// Importaciones directas (como las que ya tienes)
import { LoginComponent } from './login/login.component';
import { DashboardComponent } from './dashboard/dashboard.component';

import { RoadmapTimelineComponent } from './roadmap-timeline/roadmap-timeline.component';
import { Register } from './register/register';
import { ProgressComponent } from './progress/progress.component';
import { ProfileComponent } from './profile/profile.component';
import { CatalogComponent } from './catalog/catalog.component';
import { CourseDetailComponent } from './catalog/course-detail/course-detail.component';
import { SubscriptionComponent } from './subscription/subscription';
import { ForgotPasswordComponent } from './forgot-password/forgot-password.component';
import { ResetPasswordComponent } from './reset-password/reset-password.component';
import { SettingsComponent } from './settings/settings.component';
import { AdminDashboardComponent } from './admin-dashboard/admin-dashboard.component';
import { CallbackComponent } from './auth/callback/callback.component';

export const routes: Routes = [
  { path: '', redirectTo: '/login', pathMatch: 'full' },

  { path: 'login', component: LoginComponent },
  { path: 'register', component: Register },
  { path: 'forgot-password', component: ForgotPasswordComponent },
  { path: 'auth/callback', component: CallbackComponent },
  { path: 'dashboard', component: DashboardComponent },
  { path: 'admin/dashboard', component: AdminDashboardComponent },

  { path: 'catalog', component: CatalogComponent },
  { path: 'catalog/:slug', component: CourseDetailComponent },

  { path: 'roadmap-timeline', component: RoadmapTimelineComponent },
  { path: 'progreso', component: ProgressComponent },
  { path: 'perfil', component: ProfileComponent },
  { path: 'subscription', component: SubscriptionComponent },
  { path: 'configuracion', component: SettingsComponent },

  { path: 'reset-password/:uidb64/:token', component: ResetPasswordComponent },

  // Ruta comodín (captura cualquier ruta desconocida)
  { path: '**', redirectTo: '/login' }
];
