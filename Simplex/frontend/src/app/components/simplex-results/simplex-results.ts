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
  private readonly zeroTol = 1e-9;

  // This runs automatically whenever the parent gives us new responseData
  ngOnChanges() {
    this.currentStepIndex = 0;
  }

  // Helper to easily get the tableau for the current step
  get currentStep() {
    if (!this.responseData || !this.responseData.steps) return null;
    return this.responseData.steps[this.currentStepIndex];
  }

  get finalStep() {
    if (!this.responseData || !this.responseData.steps || this.responseData.steps.length === 0) return null;
    return this.responseData.steps[this.responseData.steps.length - 1];
  }

  get basicFinalVariables() {
    if (!this.finalStep || !this.finalStep.tableau) return [];

    const rhsIndex = this.finalStep.tableau[0]?.length - 1;
    if (rhsIndex === undefined || rhsIndex < 0) return [];

    return this.finalStep.tableau.slice(0, -1).map((row: number[], i: number) => ({
      name: this.finalStep.basicVariables[i],
      value: row[rhsIndex]
    }));
  }

  get bindingConstraints() {
    if (!this.responseData || !this.responseData.finalVariables) return [];

    const bindings: { label: string; slack: string }[] = [];
    for (const [name, value] of Object.entries(this.responseData.finalVariables)) {
      if (!name || (typeof value !== 'number')) {
        continue;
      }

      if ((name.startsWith('s_') || name.startsWith('e_')) && Math.abs(value) <= this.zeroTol) {
        const parts = name.split('_');
        const idx = Number(parts[1]);
        const label = Number.isFinite(idx) ? `Constraint ${idx}` : name;
        bindings.push({ label, slack: name });
      }
    }

    return bindings;
  }

  get pivotCount(): number {
    if (!this.responseData || !this.responseData.steps) return 0;
    return this.responseData.steps.filter((step: any) => step.stage === 'before').length;
  }

  get showPivotHighlight(): boolean {
    return this.currentStep?.stage === 'before';
  }

  get enteringVar(): string | null {
    return this.currentStep?.enteringVar ?? null;
  }

  get leavingVar(): string | null {
    return this.currentStep?.leavingVar ?? null;
  }

  get enteringReason(): string | null {
    return this.currentStep?.enteringReason ?? null;
  }

  get leavingReason(): string | null {
    return this.currentStep?.leavingReason ?? null;
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
