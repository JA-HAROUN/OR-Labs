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
    // We will call the API service here later!
  }
}
