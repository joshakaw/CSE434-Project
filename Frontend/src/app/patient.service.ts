import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, interval } from 'rxjs';
import { switchMap, startWith, tap } from 'rxjs/operators';

export interface Patient {
  id: string;
  name: string;
  symptoms: string;
  urgency: 'Emergency' | 'Urgent' | 'Non-Urgent';
  summary: string;
  department: string;
  routing: string;
  classifier_urgency: string | null;
  classifier_confidence: number | null;
  models_disagree: boolean;
  timestamp: string;
}

export interface SubmitRequest {
  name: string;
  symptoms: string;
}

@Injectable({ providedIn: 'root' })
export class PatientService {
  private http = inject(HttpClient);
  private apiUrl = '/api';

  /** Shared, live list of patients updated by polling and new submissions. */
  private patientsSubject = new BehaviorSubject<Patient[]>([]);
  public patients$ = this.patientsSubject.asObservable();

  constructor() {
    // Poll for new patients every 5 seconds
    interval(5000)
      .pipe(
        startWith(0),
        switchMap(() => this.http.get<Patient[]>(`${this.apiUrl}/patients`))
      )
      .subscribe({
        next: (patients) => this.patientsSubject.next(patients),
        error: (err) => console.error('[PatientService] Polling error:', err),
      });
  }

  /** Submit a new patient and add them to the local list immediately. */
  submitPatient(req: SubmitRequest): Observable<Patient> {
    return this.http.post<Patient>(`${this.apiUrl}/submit`, req).pipe(
      tap((newPatient) => {
        const current = this.patientsSubject.getValue();
        this.patientsSubject.next([...current, newPatient]);
      })
    );
  }
}
