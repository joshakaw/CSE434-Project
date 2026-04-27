import { Component, signal } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { MatToolbar, MatToolbarRow } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIcon } from '@angular/material/icon';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { FormsModule } from '@angular/forms';
import {
  MatNavList,
  MatList,
  MatListItem,
  MatListItemTitle,
  MatListItemIcon,
} from '@angular/material/list';

@Component({
  selector: 'app-root',
  templateUrl: './app.html',
  styleUrl: './app.scss',
  imports: [
    MatNavList,
    MatList,
    FormsModule,
    MatCheckboxModule,
    MatSidenavModule,
    RouterOutlet,
    MatToolbar,
    MatButtonModule,
    MatIcon,
    MatToolbarRow,
    MatListItem,
    MatListItemTitle,
    MatListItemIcon,
    RouterLink,
    RouterLinkActive
],
})
export class App {
  protected readonly title = signal('Frontend');
  opened: boolean = false;

  links = [
    { routerLink: '/dashboard', name: 'Dashboard (Hospital)', icon: 'dashboard' },
    { routerLink: '/chat', name: 'Chat (Patient)', icon: 'chat' },
  ];
}
