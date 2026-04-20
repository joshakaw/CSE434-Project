import {
  provideZoneChangeDetection,
  provideBrowserGlobalErrorListeners,
  importProvidersFrom,
} from '@angular/core';
import {
  platformBrowser,
  BrowserModule,
  bootstrapApplication,
} from '@angular/platform-browser';

import { AppRoutingModule } from './app/app-routing-module';
import { App } from './app/app';

bootstrapApplication(App, {
  providers: [
    importProvidersFrom(BrowserModule, AppRoutingModule),
    provideBrowserGlobalErrorListeners(),
  ],
}).catch((err) => console.error(err));
