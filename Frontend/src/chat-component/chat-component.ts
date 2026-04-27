import { Component } from '@angular/core';
import {MatInputModule} from '@angular/material/input';
import {MatFormFieldModule} from '@angular/material/form-field';
import {FormsModule} from '@angular/forms';
import { MatAnchor } from "@angular/material/button";
import { MatIcon } from '@angular/material/icon';

@Component({
  selector: 'app-chat-component',
  imports: [MatIcon, FormsModule, MatFormFieldModule, MatInputModule, MatAnchor],
  templateUrl: './chat-component.html',
  styleUrl: './chat-component.scss',
})
export class ChatComponent {}
