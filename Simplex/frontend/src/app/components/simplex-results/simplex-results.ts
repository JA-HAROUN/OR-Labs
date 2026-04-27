import { Component, Input, OnChanges } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-simplex-results',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './simplex-results.html',
  styleUrl: './simplex-results.css'
})
export class SimplexResults implements OnChanges {
  @Input() responseData: any = null;

  currentStepIndex: number = 0;

  // This runs automatically whenever the parent gives us new responseData
  ngOnChanges() {
    this.currentStepIndex = 0;
  }

  // Helper to easily get the tableau for the current step
  get currentStep() {
    if (!this.responseData || !this.responseData.steps) return null;
    return this.responseData.steps[this.currentStepIndex];
  }

  get formattedVariables() {
    if (!this.responseData || !this.responseData.finalVariables) return [];

    return Object.entries(this.responseData.finalVariables).map(([key, value]) => ({
      key: key,
      value: value as number // We promise Angular this is a number!
    }));
  }
  nextStep() {
    if (this.currentStepIndex < this.responseData.steps.length - 1) {
      this.currentStepIndex++;
    }
  }

  prevStep() {
    if (this.currentStepIndex > 0) {
      this.currentStepIndex--;
    }
  }
}
