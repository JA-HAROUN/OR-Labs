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

    // TEMPORARY DUMMY DATA
    this.finalResults = {
      status: "Optimal Solution Found",
      optimalValue: 9,
      finalVariables: { x1: 0, x2: 0, x3: 6, x4: 4, x5: 0, x6: 12 },
      headers: ["x1", "x2", "x3", "x4", "x5", "x6", "RHS"],
      steps: [
        {
          iteration: 1,
          basicVariables: ["x4", "x3", "x6", "-z"],
          // NEW: Simulate Python telling us where the pivot is!
          pivotRow: 1, // The 2nd row (index 1)
          pivotCol: 0, // The 1st column (index 0)
          tableau: [
            [0, 1, 0, 1, -2, 0, 4],
            [1, -2, 1, 0, -2, 0, 6],
            [3, 2, 0, 0, -3, 1, 12],
            [-6, 1, 0, 0, -1, 0, -9]
          ]
        }
      ]
    };
  }
}
