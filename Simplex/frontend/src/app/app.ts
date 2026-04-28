import { Component } from '@angular/core';
import { CommonModule } from '@angular/common'; // Required to use *ngIf
import { SimplexInput } from './components/simplex-input/simplex-input';
import { SimplexResults } from './components/simplex-results/simplex-results';
import { Api } from './services/api';
import { SimplexRequest, SimplexResponse } from './models/simplex.model';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, SimplexInput, SimplexResults],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class AppComponent {
  finalResults: SimplexResponse | null = null;

  constructor(private api: Api) {}

  onSolve(problemData: SimplexRequest) {
    console.log('Data received from input form:', problemData);

    this.finalResults = null;
    this.api.solveSimplex(problemData).subscribe({
      next: (response) => {
        this.finalResults = response;
      },
      error: (error) => {
        console.error('Failed to solve simplex:', error);
      }
    });
  }
}
