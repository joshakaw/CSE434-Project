import { Component, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatButtonModule } from '@angular/material/button';
import { MatIcon } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatChipsModule } from '@angular/material/chips';
import { NgClass } from '@angular/common';
import { PatientService, Patient } from '../app/patient.service';
import { inject } from '@angular/core';

@Component({
  selector: 'app-chat-component',
  imports: [
    FormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIcon,
    MatProgressSpinnerModule,
    MatChipsModule,
    NgClass,
  ],
  templateUrl: './chat-component.html',
  styleUrl: './chat-component.scss',
})
export class ChatComponent {
  private patientService = inject(PatientService);

  name = signal('');
  symptoms = signal('');
  loading = signal(false);
  errorMsg = signal('');
  result = signal<Patient | null>(null);

  submit() {
    const name = this.name().trim();
    const symptoms = this.symptoms().trim();

    if (!symptoms) {
      this.errorMsg.set('Please describe your symptoms before submitting.');
      return;
    }

    this.loading.set(true);
    this.errorMsg.set('');
    this.result.set(null);

    this.patientService
      .submitPatient({ name: name || 'Anonymous', symptoms })
      .subscribe({
        next: (patient) => {
          this.result.set(patient);
          this.loading.set(false);
        },
        error: (err) => {
          console.error(err);
          this.errorMsg.set(
            err?.error?.error ?? 'Something went wrong. Please try again.'
          );
          this.loading.set(false);
        },
      });
  }

  reset() {
    this.name.set('');
    this.symptoms.set('');
    this.result.set(null);
    this.errorMsg.set('');
  }

  urgencyClass(urgency: string): string {
    switch (urgency) {
      case 'Emergency': return 'urgency-emergency';
      case 'Urgent':    return 'urgency-urgent';
      default:          return 'urgency-non-urgent';
    }
  }
}
