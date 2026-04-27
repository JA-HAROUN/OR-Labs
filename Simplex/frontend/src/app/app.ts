import { Component } from '@angular/core';
import { CommonModule } from '@angular/common'; // Required to use *ngIf
import { SimplexInput } from './components/simplex-input/simplex-input';
import { SimplexResults } from './components/simplex-results/simplex-results';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, SimplexInput, SimplexResults],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class AppComponent {
  finalResults: any = null;

  onSolve(problemData: any) {
    console.log("Data received from input form:", problemData);

    // TEMPORARY DUMMY DATA TO TEST THE UI
    this.finalResults = {
      status: "Optimal Solution Found",
      optimalValue: 12.5,
      finalVariables: { x1: 2.5, x2: 0, s1: 0, s2: 4 },
      steps: [
        { iteration: 1, tableau: [[1, -3, -5, 0, 0, 0], [0, 1, 0, 1, 0, 4], [0, 0, 2, 0, 1, 12]] },
        { iteration: 2, tableau: [[1, -3, 0, 0, 2.5, 30], [0, 1, 0, 1, 0, 4], [0, 0, 1, 0, 0.5, 6]] }
      ]
    };
  }
}
