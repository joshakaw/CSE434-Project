import { Component, Inject } from '@angular/core';
import { NgClass } from '@angular/common';
import {
  MAT_DIALOG_DATA,
  MatDialogModule,
} from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider';
import { Patient } from '../app/patient.service';

@Component({
  selector: 'app-patient-detail-dialog',
  standalone: true,
  imports: [MatDialogModule, MatButtonModule, MatIconModule, MatDividerModule, NgClass],
  template: `
    <div class="dialog-header" [ngClass]="urgencyBg(patient.urgency)">
      <div class="dialog-name">{{ patient.name }}</div>
      <span class="urgency-badge">{{ patient.urgency }}</span>
    </div>

    <mat-dialog-content class="dialog-body">

      <!-- Disagreement warning -->
      @if (patient.models_disagree) {
        <div class="disagree-banner">
          <mat-icon class="warn-icon">warning</mat-icon>
          <span>
            <strong>Models disagree.</strong>
            Gemini assessed <strong>{{ patient.urgency }}</strong> but the deep learning
            model assessed <strong>{{ patient.classifier_urgency }}</strong>.
            Manual review recommended.
          </span>
        </div>
      }

      <!-- Deep learning row -->
      @if (patient.classifier_urgency) {
        <div class="detail-row">
          <span class="detail-label">
            <mat-icon class="row-icon">psychology</mat-icon>
            Deep Learning Model
          </span>
          <span class="detail-value">
            <span class="inline-badge" [ngClass]="urgencyBg(patient.classifier_urgency)">
              {{ patient.classifier_urgency }}
            </span>
            <span class="muted">{{ patient.classifier_confidence }}% confidence</span>
          </span>
        </div>
        <mat-divider />
      }

      <!-- Department -->
      <div class="detail-row">
        <span class="detail-label">
          <mat-icon class="row-icon">local_hospital</mat-icon>
          Department
        </span>
        <span class="detail-value">{{ patient.department }}</span>
      </div>
      @if (patient.routing) {
        <p class="routing-note">{{ patient.routing }}</p>
      }
      <mat-divider />

      <!-- Gemini summary -->
      <div class="detail-row">
        <span class="detail-label">
          <mat-icon class="row-icon">auto_awesome</mat-icon>
          Gemini Summary
        </span>
      </div>
      <p class="detail-para">{{ patient.summary }}</p>
      <mat-divider />

      <!-- Reported symptoms -->
      <div class="detail-row">
        <span class="detail-label">
          <mat-icon class="row-icon">description</mat-icon>
          Reported Symptoms
        </span>
      </div>
      <p class="detail-para muted">{{ patient.symptoms }}</p>
      <mat-divider />

      <!-- Submitted time -->
      <div class="detail-row">
        <span class="detail-label">
          <mat-icon class="row-icon">schedule</mat-icon>
          Submitted
        </span>
        <span class="detail-value muted">{{ formatTime(patient.timestamp) }}</span>
      </div>

    </mat-dialog-content>

    <mat-dialog-actions align="end">
      <button mat-flat-button mat-dialog-close>Close</button>
    </mat-dialog-actions>
  `,
  styles: [`
    .dialog-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 20px 24px 16px;
      border-radius: 4px 4px 0 0;
    }
    .dialog-name { font-size: 1.3rem; font-weight: 700; color: #fff; }
    .urgency-badge {
      padding: 4px 14px;
      border-radius: 20px;
      background: rgba(255,255,255,0.25);
      color: #fff;
      font-size: 0.78rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }
    .bg-emergency { background: #b71c1c; }
    .bg-urgent    { background: #e65100; }
    .bg-nonurgent { background: #1b5e20; }

    .dialog-body { padding: 8px 0; min-width: 380px; max-width: 520px; }

    .detail-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 10px 0 4px;
      gap: 12px;
    }
    .detail-label {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 0.72rem;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      font-weight: 700;
      opacity: 0.55;
      flex-shrink: 0;
    }
    .row-icon { font-size: 15px; width: 15px; height: 15px; }
    .detail-value { font-size: 0.95rem; text-align: right; }
    .detail-para  { font-size: 0.95rem; line-height: 1.55; margin: 4px 0 10px; }

    .inline-badge {
      display: inline-block;
      padding: 2px 10px;
      border-radius: 20px;
      color: #fff;
      font-size: 0.75rem;
      font-weight: 700;
      text-transform: uppercase;
      margin-right: 6px;
    }
    .routing-note {
      font-size: 0.82rem;
      font-style: italic;
      opacity: 0.6;
      margin: 2px 0 10px;
      line-height: 1.4;
    }
    .muted { opacity: 0.6; }

    .disagree-banner {
      display: flex;
      align-items: flex-start;
      gap: 10px;
      background: rgba(249, 168, 37, 0.12);
      border: 1px solid rgba(249, 168, 37, 0.45);
      border-radius: 8px;
      padding: 10px 14px;
      margin-bottom: 8px;
      font-size: 0.88rem;
      line-height: 1.5;
      color: #f9a825;
    }
    .warn-icon { font-size: 18px; width: 18px; height: 18px; flex-shrink: 0; margin-top: 1px; }
  `],
})
export class PatientDetailDialogComponent {
  constructor(@Inject(MAT_DIALOG_DATA) public patient: Patient) {}

  urgencyBg(urgency: string): string {
    switch (urgency) {
      case 'Emergency': return 'bg-emergency';
      case 'Urgent':    return 'bg-urgent';
      default:          return 'bg-nonurgent';
    }
  }

  formatTime(ts: string): string {
    return new Date(ts).toLocaleString();
  }
}
