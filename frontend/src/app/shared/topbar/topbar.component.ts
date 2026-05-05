import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { NotificationsComponent } from '../notifications/notifications.component';

@Component({
  selector: 'app-topbar',
  standalone: true,
  imports: [CommonModule, RouterLink, NotificationsComponent],
  templateUrl: './topbar.component.html',
  styleUrls: ['./topbar.component.css']
})
export class TopbarComponent {
  @Input() userProfile: any;
  @Input() title: string = ''; // Opcional, para páginas que necesiten un título a la izquierda (ej. Perfil)
}
