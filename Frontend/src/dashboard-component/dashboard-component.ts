import { Component } from '@angular/core';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatCard, MatCardTitle, MatCardContent } from "@angular/material/card";

@Component({
  selector: 'app-dashboard-component',
  imports: [MatGridListModule, MatCard, MatCardTitle, MatCardContent],
  templateUrl: './dashboard-component.html',
  styleUrl: './dashboard-component.css',
})
export class DashboardComponent {
  public inpatients : Array<{name: string, status: string}>

  constructor(){
    this.inpatients = [
      {name: "Adam", status: "Urgent"}, {name: "Bill", status: "Non-Urgent"}
    ]
  }
}
