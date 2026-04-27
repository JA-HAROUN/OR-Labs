
export interface SimplexRequest {
  objectiveType: string;       // 'Maximize' or 'Minimize'
  numVariables: number;
  numConstraints: number;
  objectiveCoefficients: number[];
  constraints: {
    coefficients: number[];
    type: string;              // '<=', '>=', '='
    rhs: number;
  }[];
  variableRestrictions: string[]; // e.g., ['>=0', 'free']
}

export interface SimplexStep {
  iteration: number;
  tableau: number[][];
  basicVariables: string[];
  pivotRow?: number;
  pivotCol?: number;
}

export interface SimplexResponse {
  status: string;
  optimalValue: number;
  finalVariables: any;
  steps: SimplexStep[];
}
