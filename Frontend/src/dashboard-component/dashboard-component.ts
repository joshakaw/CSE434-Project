import { Component } from '@angular/core';
import { MatGridListModule } from '@angular/material/grid-list';
import {
  MatCard,
  MatCardTitle,
  MatCardContent,
  MatCardHeader,
  MatCardAvatar,
  MatCardActions,
  MatCardSubtitle,
} from '@angular/material/card';
import { MatAnchor } from '@angular/material/button';
import { MatRipple } from '@angular/material/core';

export enum Urgency {
  Urgent,
  NonUrgent,
}

@Component({
  selector: 'app-dashboard-component',
  imports: [
    MatGridListModule,
    MatCard,
    MatCardTitle,
    MatCardContent,
    MatCardHeader,
    MatCardAvatar,
    MatCardHeader,
    MatCardActions,
    MatAnchor,
    MatCardSubtitle,
    MatRipple,
  ],
  templateUrl: './dashboard-component.html',
  styleUrl: './dashboard-component.scss',
})
export class DashboardComponent {
  public inpatients: Array<{ name: string; status: Urgency; summary: string }>;
  public Urgency = Urgency;

  constructor() {
    this.inpatients = [
      {
        name: 'Adam',
        status: Urgency.NonUrgent,
        summary: 'Patient presents symptoms of common cold.',
      },
      {
        name: 'Bella',
        status: Urgency.Urgent,
        summary: 'Patient complaining of worsening asthma symptoms.',
      },
      {
        name: 'Charlie',
        status: Urgency.Urgent,
        summary: 'Cardiac arrhythmia detected on telemetry monitor.',
      },
      {
        name: 'Diana',
        status: Urgency.NonUrgent,
        summary: 'Routine follow-up for stable hypertension.',
      },
      {
        name: 'Edward',
        status: Urgency.Urgent,
        summary: 'Compound fracture of the left tibia from a fall.',
      },
      {
        name: 'Fiona',
        status: Urgency.Urgent,
        summary: 'Persistent high fever unresponsive to antipyretics.',
      },
      {
        name: 'George',
        status: Urgency.Urgent,
        summary: 'Sudden onset of neurological deficits, suspected stroke.',
      },
      {
        name: 'Hannah',
        status: Urgency.NonUrgent,
        summary: 'Minor laceration on hand requiring sutures.',
      },
      {
        name: 'Ian',
        status: Urgency.Urgent,
        summary: 'Severe abdominal pain with suspected appendicitis.',
      },
      {
        name: 'Julia',
        status: Urgency.Urgent,
        summary: 'Acute anaphylactic reaction to medication.',
      },
    ];
  }
}
