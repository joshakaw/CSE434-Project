import { Component, inject } from '@angular/core';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatRipple } from '@angular/material/core';
import { MatDialog } from '@angular/material/dialog';
import { AsyncPipe, NgClass } from '@angular/common';
import { map } from 'rxjs/operators';
import { BreakpointObserver, Breakpoints } from '@angular/cdk/layout';
import { PatientService, Patient } from '../app/patient.service';
import { PatientDetailDialogComponent } from './patient-detail-dialog';

const URGENCY_ORDER: Record<string, number> = {
  'Emergency': 0,
  'Urgent':    1,
  'Non-Urgent': 2,
};

function sortPatients(patients: Patient[]): Patient[] {
  return [...patients].sort((a, b) => {
    const urgencyDiff =
      (URGENCY_ORDER[a.urgency] ?? 3) - (URGENCY_ORDER[b.urgency] ?? 3);
    if (urgencyDiff !== 0) return urgencyDiff;
    // Within same urgency: oldest submission first (waiting longest)
    return new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime();
  });
}

function urgencyClass(urgency: string): string {
  switch (urgency) {
    case 'Emergency': return 'urgent emergency';
    case 'Urgent':    return 'urgent';
    default:          return '';
  }
}

@Component({
  selector: 'app-dashboard-component',
  imports: [MatGridListModule, MatRipple, AsyncPipe, NgClass],
  templateUrl: './dashboard-component.html',
  styleUrl: './dashboard-component.scss',
})
export class DashboardComponent {
  private patientService = inject(PatientService);
  private dialog = inject(MatDialog);
  private breakpointObserver = inject(BreakpointObserver);

  /** Sorted live patient list. */
  patients$ = this.patientService.patients$.pipe(
    map(sortPatients)
  );

  cols$ = this.breakpointObserver
    .observe([
      Breakpoints.XSmall,
      Breakpoints.Small,
      Breakpoints.Medium,
      Breakpoints.Large,
      Breakpoints.XLarge,
    ])
    .pipe(
      map((result) => {
        if (
          result.breakpoints[Breakpoints.XSmall] ||
          result.breakpoints[Breakpoints.Small]
        )
          return 1;
        if (result.breakpoints[Breakpoints.Medium]) return 3;
        return 4;
      })
    );

  urgencyClass = urgencyClass;

  openDetail(patient: Patient): void {
    this.dialog.open(PatientDetailDialogComponent, {
      data: patient,
      width: '540px',
      maxWidth: '95vw',
    });
  }
}
