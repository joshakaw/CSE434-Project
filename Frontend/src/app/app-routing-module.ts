import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { DashboardComponent } from '../dashboard-component/dashboard-component';
import { ChatComponent } from '../chat-component/chat-component';

const routes: Routes = [
  {
    path: '',
    pathMatch: "full",
    redirectTo: 'dashboard'
  },
  {
    path: 'dashboard',
    component: DashboardComponent,
  },
  {
    path: 'chat',
    component: ChatComponent
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
