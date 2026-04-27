import {Component, EventEmitter, Output} from '@angular/core';
import {CommonModule} from '@angular/common';
import {FormArray, FormBuilder, FormGroup, ReactiveFormsModule, Validators} from '@angular/forms';

@Component({
  selector: 'app-simplex-input',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './simplex-input.html',
  styleUrl: './simplex-input.css',
})
export class SimplexInput {
  @Output() solveEvent = new EventEmitter<any>();
  problemForm!: FormGroup;
  gridGenerated: boolean = false; // Tracks if the matrix is visible

  constructor(private fb: FormBuilder) {
  }

  ngOnInit() {
    this.problemForm = this.fb.group({
      objectiveType: ['Maximize', Validators.required],
      numVariables: [2, [Validators.required, Validators.min(1)]],
      numConstraints: [2, [Validators.required, Validators.min(1)]],
      // These arrays will hold our dynamic matrix inputs
      objectiveCoefficients: this.fb.array([]),
      constraints: this.fb.array([]),
      variableRestrictions: this.fb.array([])
    });
  }
  get objectiveCoefficients() { return this.problemForm.get('objectiveCoefficients') as FormArray; }
  get constraints() { return this.problemForm.get('constraints') as FormArray; }
  get variableRestrictions() { return this.problemForm.get('variableRestrictions') as FormArray; }
  getCoefficients(constraintIndex: number): FormArray {
    return this.constraints.at(constraintIndex).get('coefficients') as FormArray;
  }
  generateGrid() {
    const vars = this.problemForm.value.numVariables;
    const cons = this.problemForm.value.numConstraints;

    // 1. Clear existing arrays (in case the user changes the numbers and clicks generate again)
    this.objectiveCoefficients.clear();
    this.constraints.clear();
    this.variableRestrictions.clear();

    // 2. Build Objective Function Row
    for (let i = 0; i < vars; i++) {
      this.objectiveCoefficients.push(this.fb.control(0, Validators.required));
      // Default all variables to Non-Negative (>=0)
      this.variableRestrictions.push(this.fb.control('>=0', Validators.required));
    }

    // 3. Build Constraint Rows
    for (let i = 0; i < cons; i++) {
      const constraintRow = this.fb.group({
        coefficients: this.fb.array([]),
        type: ['<=', Validators.required], // Default constraint type
        rhs: [0, Validators.required]
      });

      // Add coefficients to this specific constraint row
      const coefArray = constraintRow.get('coefficients') as FormArray;
      for (let j = 0; j < vars; j++) {
        coefArray.push(this.fb.control(0, Validators.required));
      }

      this.constraints.push(constraintRow);
    }

    this.gridGenerated = true;
  }
  onSubmit() {
    if (this.problemForm.valid) {
      this.solveEvent.emit(this.problemForm.value);
    }
  }
}
