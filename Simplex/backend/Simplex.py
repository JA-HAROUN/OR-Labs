from enum import Enum
import math
import numpy as np
from rich.console import Console
from rich.table import Table

"""
    Degeneracy:
        In the application of the feasibility condition of the simplex method,
        a tie for the minimum ratio may occur and can be broken arbitrarily.
            => When this happens, at least one basic variable will be zero in the next iteration,
                and the new solution is said to be degenerate.
        Degeneracy can cause the simplex iterations to cycle indefinitely,
        thus never terminating the algorithm.
        The condition also reveals the possibility of at least one redundant constraint.
        
        To See: Hamdy Taha's Reference page 118 + Section 3.7 page 138

"""

# Enums
class Var_Type(Enum):
    NULL = 0
    NORMAL = 1
    SLACK = 2
    SURPLUS = 3
    ARTIFICIAL = 4

class Var_Constraints(Enum):
    NON_NEGATIVE = 1
    UNRESTRICTED = 2

class Optimization_Type(Enum):
    NULL = 0
    MINIMIZATION = 1
    MAXIMIZATION = 2
    
class Simplex_Solution(Enum):
    NULL = 0
    OPTIMAL = 1
    UNBOUNDED = 2
    UNFEASIBLE = 3


class Simplex:
    
    def __init__(self, goal=Optimization_Type.NULL, obj_func_coeffs=(), constraints_vars_coeffs=(), RHS=(), operators=(),var_constraints=None):
        obj_func_coeffs = np.asarray(obj_func_coeffs, dtype=float)
        constraints_vars_coeffs = np.asarray(constraints_vars_coeffs, dtype=float)
        RHS = np.asarray(RHS, dtype=float)
        operators = list(operators)

        if constraints_vars_coeffs.size == 0:
            constraints_vars_coeffs = np.empty((0, 0), dtype=float)
        elif constraints_vars_coeffs.ndim == 1:
            constraints_vars_coeffs = constraints_vars_coeffs.reshape(1, -1)

        # States
        self.num_of_constraints = constraints_vars_coeffs.shape[0]
        self.num_of_variables = constraints_vars_coeffs.shape[1]
        
        if var_constraints is None:
            self.var_constraints = [Var_Constraints.NON_NEGATIVE] * self.num_of_variables
        else:
            if len(var_constraints) != self.num_of_variables:
                raise ValueError("var_constraints must match number of variables")
            self.var_constraints = list(var_constraints)
        
        self.goal = goal
        
        self.obj_func_coeffs = obj_func_coeffs.copy()
        self.output = np.array([0.0], dtype=float)     # has just one value
        self.variables = [f"x_{i + 1}" for i in range(self.num_of_variables)]  # x_1, x_2, x_3, ...
        self.constraints_vars_coeffs = constraints_vars_coeffs.copy()    # it is array of arrays
        self.RHS = RHS.copy()
        self.operators = list(operators)
        
        self.basic_vars = []
        self.non_basic_vars = self.variables.copy()
        
        self.degenerate_count = 0
        
        self.slacks_num = 0
        self.surplus_num = 0
        self.artificial_num = 0
        
        self.phase_one_flag = False
        
        self.solution = Simplex_Solution.NULL
        
        self.finished   = False
        self.unbounded  = False   # True when ratio_test finds no positive pivot element
        
        # Frontend API tracking
        self.steps = []
        self.iteration = 0
        
        # Main Terminal tracking
        self.iteration_history = {}
        self.last_tableau_data = {}
        self.console = Console()

    # Clears previous iteration snapshots before starting a new run.
    def reset_history(self):
        self.iteration_history = {}

    # Rebuilds the non-basic variable list from the current basis.
    def update_non_basic_variables(self):
        active_variables = self.variables[:len(self.obj_func_coeffs)]
        self.non_basic_vars = [var for var in active_variables if var not in self.basic_vars]

    # Saves one tableau snapshot for Terminal (coefficients, RHS, basis, output).
    def record_history(self, leaving_var_row=None):
        self.update_non_basic_variables()
        iteration_number = len(self.iteration_history) + 1
        self.iteration_history[iteration_number] = {
            "coeffs": self.constraints_vars_coeffs.copy(),
            "RHS": self.RHS.copy(),
            "output": float(self.output[0]),
            "basic_vars": self.basic_vars.copy(),
            "non_basic_vars": self.non_basic_vars.copy(),
            "ratio_row": leaving_var_row,
        }
    
    # Stores the final solver state for API/UI consumption.
    def save_result(self):
        self.last_tableau_data = {
            "solution_status": self.solution,
            "variables": self.variables.copy(),
            "objective_coeffs": self.obj_func_coeffs.copy(),
            "coeffs": self.constraints_vars_coeffs.copy(),
            "RHS": self.RHS.copy(),
            "output": float(self.output[0]),
            "basic_vars": self.basic_vars.copy(),
            "non_basic_vars": self.non_basic_vars.copy(),
        }

    # Formats numbers for readable output tables.
    def _fmt_value(self, value):
        value = float(value)
        if value.is_integer():
            return str(int(value))
        return f"{value:.4g}"

    # Builds one Rich table for a simplex tableau (optionally with z-row).
    def _build_tableau_table(self, col_names, basic_vars, coeffs, rhs, z_coeffs=None, z_val=None, title=None):
        table = Table(title=title, show_lines=False)
        table.add_column("BV", justify="center")
        for name in col_names:
            table.add_column(str(name), justify="right")
        table.add_column("RHS", justify="right")

        for i, bv in enumerate(basic_vars):
            row = [str(bv)] + [self._fmt_value(v) for v in coeffs[i]] + [self._fmt_value(rhs[i])]
            table.add_row(*row)

        if z_coeffs is not None and z_val is not None:
            z_row = ["z"] + [self._fmt_value(v) for v in z_coeffs] + [self._fmt_value(z_val)]
            table.add_row(*z_row)

        return table

    # Prints all saved tableau snapshots after solving.
    def print_iteration_history(self):
        self.console.rule("ITERATION HISTORY")

        if len(self.iteration_history) == 0:
            self.console.print("  No history recorded.\n")
            return

        for iteration_number in sorted(self.iteration_history.keys()):
            history = self.iteration_history[iteration_number]
            coeffs = history["coeffs"]
            rhs = history["RHS"]
            basic_vars = history["basic_vars"]

            col_names = self.variables[:coeffs.shape[1]]
            self.console.print(f"\n  Iteration {iteration_number} history is:")
            self.console.print(f"    Ratio row      : {history['ratio_row']}")
            self.console.print(f"    Output (z)     : {self._fmt_value(history['output'])}")
            self.console.print(f"    Basic vars     : {basic_vars}")
            self.console.print(f"    Non-basic vars : {history['non_basic_vars']}")

            table = self._build_tableau_table(
                col_names=col_names,
                basic_vars=basic_vars,
                coeffs=coeffs,
                rhs=rhs,
            )
            self.console.print(table)
            self.console.print()
            
    # Snapshots tableau state for the Frontend API
    def _snapshot_tableau(self):
        tableau = []
        for i in range(self.num_of_constraints):
            row = self.constraints_vars_coeffs[i].tolist()
            row.append(float(self.RHS[i]))
            tableau.append(row)
        z_val = float(self.output[0]) if hasattr(self.output, "__len__") else float(self.output)
        z_row = self.obj_func_coeffs.tolist()
        z_row.append(z_val)
        tableau.append(z_row)
        return tableau

    # Records the step data object expected by Angular API
    def record_step(self, pivot_row=None, pivot_col=None, iteration=None, stage="after", entering_var=None, leaving_var=None, entering_reason=None, leaving_reason=None):
        if iteration is None:
            if stage == "after":
                self.iteration += 1
            iteration = self.iteration

        self.steps.append({
            "iteration": iteration,
            "tableau": self._snapshot_tableau(),
            "basicVariables": self.basic_vars + ["z"],
            "pivotRow": pivot_row,
            "pivotCol": pivot_col,
            "stage": stage,
            "enteringVar": entering_var,
            "leavingVar": leaving_var,
            "enteringReason": entering_reason,
            "leavingReason": leaving_reason,
        })

    # Builds final response payload for Frontend API
    def build_response(self):
        headers = self.variables[:len(self.obj_func_coeffs)] + ["RHS"]
        final_vars = {name: 0.0 for name in headers[:-1]}

        for i, bv in enumerate(self.basic_vars):
            if bv in final_vars:
                final_vars[bv] = float(self.RHS[i])

        z_val = float(self.output[0]) if hasattr(self.output, "__len__") else float(self.output)
        return {
            "status": self.solution.name if isinstance(self.solution, Simplex_Solution) else str(self.solution),
            "optimalValue": z_val,
            "finalVariables": final_vars,
            "headers": headers,
            "steps": self.steps,
        }

    # Applies one pivot operation to constraints, RHS, and objective row.
    def pivoting(self, row_pivot, col_pivot):
        # Step 1
        pivot = self.constraints_vars_coeffs[row_pivot][col_pivot]
        if (pivot != 1):
            self.constraints_vars_coeffs[row_pivot] = self.constraints_vars_coeffs[row_pivot] / pivot
            self.RHS[row_pivot] = self.RHS[row_pivot] / pivot
            
        for i in range(self.num_of_constraints):
            if (i == row_pivot):
                continue
            # Step 2
            factor = self.constraints_vars_coeffs[i][col_pivot]
            # Step 3
            self.constraints_vars_coeffs[i] = self.constraints_vars_coeffs[i] + (self.constraints_vars_coeffs[row_pivot] * -factor)
            self.RHS[i] = self.RHS[i] - (self.RHS[row_pivot] * factor)
        
        # Step 5
        factor = self.obj_func_coeffs[col_pivot] / self.constraints_vars_coeffs[row_pivot][col_pivot]
        
        self.obj_func_coeffs = self.obj_func_coeffs + (self.constraints_vars_coeffs[row_pivot] * -factor)
          
        self.output = self.output - (self.RHS[row_pivot] * factor)
        
    # Selects leaving row using the minimum positive ratio test.
    def ratio_test(self, column_index):
        row = -1
        min_ratio = float('inf')

        for i, rhs_value in enumerate(self.RHS):
            divisor = self.constraints_vars_coeffs[i][column_index]
            
            if divisor > 0:
                current_ratio = rhs_value / divisor
                
                if current_ratio < min_ratio:
                    min_ratio = current_ratio
                    row = i
                
                elif current_ratio == min_ratio:
                    # We have a tie for the minimum ratio
                    # In case of a tie, we choose the row with the smallest index (leftmost)
                    if row == -1 or i < row:
                        row = i
                        
        return row

    def ratio_test_details(self, column_index):
        row = -1
        min_ratio = float('inf')
        degenerate = False
        ratios = []

        for i, rhs_value in enumerate(self.RHS):
            divisor = self.constraints_vars_coeffs[i][column_index]

            if divisor > 0:
                current_ratio = rhs_value / divisor
                ratios.append((i, current_ratio))

                if current_ratio < min_ratio:
                    min_ratio = current_ratio
                    row = i
                    degenerate = False
                elif current_ratio == min_ratio:
                    degenerate = True

        return row, min_ratio, degenerate, ratios
    
    # Checks if all reduced costs satisfy optimality for current goal.
    def goal_achieved(self):
        # In phase 2, artificial columns are skipped
        # a leftover positive coefficient there does not mean the solution is not optimal.
        indices = self.real_indices()

        if self.goal == Optimization_Type.MAXIMIZATION:
            return all(self.obj_func_coeffs[j] >= 0 for j in indices)
        elif self.goal == Optimization_Type.MINIMIZATION:
            return all(self.obj_func_coeffs[j] <= 0 for j in indices)

        return True
    
    # Returns columns allowed to enter the basis.
    def real_indices(self):
        if self.phase_one_flag:
            return list(range(len(self.obj_func_coeffs)))
        return [j for j, name in enumerate(self.variables[:len(self.obj_func_coeffs)])
                if not name.startswith("a_")]

    # Picks entering variable index (most negative for max, most positive for min).
    def choose_entering_var(self):
        entering_var_index = -1
        indices = self.real_indices()

        if self.goal == Optimization_Type.MAXIMIZATION:
            best = None
            for j in indices:
                if self.obj_func_coeffs[j] < 0:
                    if best is None or self.obj_func_coeffs[j] < self.obj_func_coeffs[best]:
                        best = j
            if best is not None:
                entering_var_index = best
            else:
                self.finished = True

        elif self.goal == Optimization_Type.MINIMIZATION:
            best = None
            for j in indices:
                if self.obj_func_coeffs[j] > 0:
                    if best is None or self.obj_func_coeffs[j] > self.obj_func_coeffs[best]:
                        best = j
            if best is not None:
                entering_var_index = best
            else:
                self.finished = True

        return entering_var_index

    # Adds one auxiliary column and updates metadata/basis when needed.
    def add_auxiliary_variable(self, row_index, var_type):
        if var_type == Var_Type.SLACK:
            self.slacks_num += 1
            new_var = f"s_{self.slacks_num}"
            column_value = 1.0
            add_to_basis = True
        elif var_type == Var_Type.SURPLUS:
            self.surplus_num += 1
            new_var = f"e_{self.surplus_num}"
            column_value = -1.0
            add_to_basis = False
        elif var_type == Var_Type.ARTIFICIAL:
            self.artificial_num += 1
            new_var = f"a_{self.artificial_num}"
            column_value = 1.0
            add_to_basis = True
        else:
            raise ValueError(f"Unsupported variable type: {var_type}")

        if add_to_basis:
            self.basic_vars.append(new_var)

        self.variables.append(new_var)
        self.obj_func_coeffs = np.append(self.obj_func_coeffs, 0.0)

        new_column = np.zeros((self.num_of_constraints, 1), dtype=float)
        new_column[row_index, 0] = column_value
        self.constraints_vars_coeffs = np.hstack((self.constraints_vars_coeffs, new_column))
    
    # Expands all constraints with slack/surplus/artificial variables.
    def add_variables(self):
        for i, _ in enumerate(self.constraints_vars_coeffs) :
            operator = self.operators[i]
            if operator == "<=":
                self.add_auxiliary_variable(i, Var_Type.SLACK)

            elif operator == ">=":
                self.add_auxiliary_variable(i, Var_Type.SURPLUS)
                self.add_auxiliary_variable(i, Var_Type.ARTIFICIAL)

            elif operator == "=":
                self.add_auxiliary_variable(i, Var_Type.ARTIFICIAL)
            else :
                raise ValueError(f"Unsupported operator: {operator}")
            
    def handle_free_variables(self):
        new_obj = []
        new_constraints = []

        # Initialize new constraints matrix
        for _ in range(self.num_of_constraints):
            new_constraints.append([])

        new_variables = []

        for j in range(self.num_of_variables):
            if self.var_constraints[j] == Var_Constraints.UNRESTRICTED:
                # Replace x_j = u_j - v_j

                # Objective function
                new_obj.append(self.obj_func_coeffs[j])   # u_j
                new_obj.append(-self.obj_func_coeffs[j])  # v_j

                # Constraints
                for i in range(self.num_of_constraints):
                    coeff = self.constraints_vars_coeffs[i][j]
                    new_constraints[i].append(coeff)    # u_j
                    new_constraints[i].append(-coeff)   # v_j

                # Variable names
                new_variables.append(f"u_{j+1}")
                new_variables.append(f"v_{j+1}")

            else:
                # Keep as is
                new_obj.append(self.obj_func_coeffs[j])

                for i in range(self.num_of_constraints):
                    new_constraints[i].append(self.constraints_vars_coeffs[i][j])

                new_variables.append(f"x_{j+1}")

        # Convert back to numpy
        self.obj_func_coeffs = np.array(new_obj, dtype=float)
        self.constraints_vars_coeffs = np.array(new_constraints, dtype=float)
        self.variables = new_variables
        self.num_of_variables = len(new_variables)

    # Eliminates basic-variable coefficients from the objective row.
    def canonicalize_objective(self):
        for i, basic_var in enumerate(self.basic_vars):
            if basic_var not in self.variables[:len(self.obj_func_coeffs)]:
                continue

            col_index = self.variables.index(basic_var)
            pivot_coeff = self.constraints_vars_coeffs[i][col_index]
            if abs(pivot_coeff) <= 1e-12:
                continue

            coeff_in_obj = self.obj_func_coeffs[col_index]
            if abs(coeff_in_obj) <= 1e-12:
                continue

            factor = coeff_in_obj / pivot_coeff
            self.obj_func_coeffs = self.obj_func_coeffs - factor * self.constraints_vars_coeffs[i]
            self.output = self.output - factor * self.RHS[i]

    # Main simplex loop for one phase: enter, leave, pivot, record.
    def run_simplex_iterations(self, phase_label):
        iteration = 0
        while (not self.goal_achieved()):
            iteration += 1
            entering_var_index = self.choose_entering_var()

            if self.finished:
                break

            entering_var_name = self.variables[entering_var_index]
            entering_value = self.obj_func_coeffs[entering_var_index]
            entering_reason = f"Most positive reduced cost ({entering_value:.4g})" if self.goal == Optimization_Type.MINIMIZATION else f"Most negative reduced cost ({entering_value:.4g})"

            leaving_var_row, min_ratio, degenerate, ratios = self.ratio_test_details(entering_var_index)
            leaving_var_name = self.basic_vars[leaving_var_row] if leaving_var_row != -1 else ""

            # if ratio_test found no positive element -> unbounded
            if leaving_var_row == -1:
                self.unbounded = True
                self.record_history(leaving_var_row)
                break

            ratio_parts = [f"R{i + 1}: {r:.4g}" for i, r in ratios]
            ratio_text = ", ".join(ratio_parts) if ratio_parts else "No positive ratios"
            leaving_reason = f"Minimum ratio test → {ratio_text}; min = {min_ratio:.4g}"
            if degenerate:
                leaving_reason += " (tie/degenerate)"

            self.record_step(
                pivot_row=leaving_var_row,
                pivot_col=entering_var_index,
                stage="before",
                entering_var=entering_var_name,
                leaving_var=leaving_var_name,
                entering_reason=entering_reason,
                leaving_reason=leaving_reason,
            )

            # swap entering with leaving
            self.basic_vars[leaving_var_row] = entering_var_name

            self.pivoting(leaving_var_row, entering_var_index)
            self.record_step(stage="after")

            # Check for degeneracy
            self.check_degeneracy()

            self.record_history(leaving_var_row)
            
            print(f"  ▶  {phase_label} | Iteration {iteration}")
            print(f"     Entering : {entering_var_name}   →   Leaving : {leaving_var_name}")

    # Phase 1: build and solve auxiliary objective to test feasibility.
    def run_phase_one(self):
        self.phase_one_flag = True

        old_objective_coeffs = self.obj_func_coeffs.copy()
        old_goal = self.goal

        new_objective_coeffs = np.zeros_like(self.obj_func_coeffs, dtype=float)
        artificial_indices = [i for i, var_name in enumerate(self.variables) if var_name.startswith("a_")]
        new_objective_coeffs[artificial_indices] = -1.0
        new_goal = Optimization_Type.MINIMIZATION

        self.obj_func_coeffs = new_objective_coeffs
        self.goal = new_goal

        self.canonicalize_objective()
        self.record_step(stage="initial")

        print("\n" + "═" * 60)
        print("  PHASE 1  —  Minimize artificial variables  (W → 0)")
        print("═" * 60)

        # Run the simplex algorithm for phase one
        self.run_simplex_iterations("Phase 1")

        # Check the result of phase one
        self.check_failure()
        if self.solution == Simplex_Solution.UNFEASIBLE:
            return

        self.phase_one_flag = False
        self.obj_func_coeffs = old_objective_coeffs
        self.goal = old_goal
        self.output = np.array([0.0], dtype=float)

        # Re-canonicalize: the restored objective may have non-zero
        # coefficients for variables that are now basic after phase 1.
        self.canonicalize_objective()
        
    # Phase 2: optimize original objective using the feasible basis.
    def run_phase_two(self):
        print("\n" + "═" * 60)
        print("  PHASE 2  —  Optimize original objective")
        print("═" * 60)
        self.record_step(stage="initial")
        
        self.run_simplex_iterations("Phase 2")
            
        # Check the result of phase two
        self.check_failure()
        
    # Orchestrates full solve flow: setup, phase 1/2, history, final result.
    def run_program(self):
        self.obj_func_coeffs = -self.obj_func_coeffs
        self.reset_history()

        self.handle_free_variables()
        self.add_variables()
        self.record_step(iteration=0, stage="initial")
        self.record_history()

        print("\n" + "═" * 60)
        print("  INITIAL TABLEAU  —  After adding auxiliary variables")
        print("═" * 60)

        # Check phase 1 if there are artificial variables
        if self.artificial_num >= 1:
            self.run_phase_one()
            if (self.solution == Simplex_Solution.UNFEASIBLE):
                self.print_iteration_history()
                return

        # Do phase 2 if phase 1 was okay
        self.run_phase_two()

        self.print_iteration_history()
        
        self.save_result()
    
    # Sets final status (unfeasible, unbounded, or optimal).
    def check_failure(self):
        # Phase 1 is infeasible if a basic artificial variable stays positive.
        if self.phase_one_flag:
            infeasible = any(
                var_name.startswith("a_") and self.RHS[i] > 1e-8
                for i, var_name in enumerate(self.basic_vars)
            )
            if infeasible:
                self.solution = Simplex_Solution.UNFEASIBLE
                return

        # Unboundedness check
        if self.unbounded:
            self.solution = Simplex_Solution.UNBOUNDED
            return

        # Optimality check
        if self.finished or self.goal_achieved():
            self.solution = Simplex_Solution.OPTIMAL
        
    # Counts degenerate pivots (when any basic RHS becomes zero).
    def check_degeneracy(self):
        # A solution is degenerate if at least one basic variable is zero.
        self.degenerate_count += 1
        return np.any(self.RHS == 0)


if __name__ == "__main__":

    def run_case(title, expected, **kwargs):
        """Helper: run one simplex test then print actual vs expected summary."""
        print("\n" + "█" * 60)
        print(f"  TEST CASE : {title}")
        print("█" * 60)

        s = Simplex(**kwargs)
        s.run_program()

        def fmt_num(value):
            value = float(value)
            if value.is_integer():
                return str(int(value))
            return f"{value:.6g}"

        def extract_decision_values(simplex_obj, original_var_count):
            result = {f"x_{i + 1}": 0.0 for i in range(original_var_count)}
            for bv, rhs in zip(simplex_obj.basic_vars, simplex_obj.RHS):
                if bv in result:
                    result[bv] = float(rhs)
            return result

        original_var_count = len(kwargs.get("obj_func_coeffs", []))
        decision_values = extract_decision_values(s, original_var_count)
        z_value = float(s.last_tableau_data.get("output", s.output[0]))

        ordered_vars = ", ".join(
            [f"{name}={fmt_num(val)}" for name, val in sorted(decision_values.items())]
        )
        print(
            f"  Result   : status={s.solution.name}, z={fmt_num(z_value)}, {ordered_vars}"
        )
        print(f"  Expected : {expected}")

    # ── Case 1: Maximization, all ≤ (Hamdy Taha classic) ────────────────────
    run_case(
        "Maximization — all ≤  (3×2, Hamdy Taha)",
        expected="status=OPTIMAL, z=10, x_1=2, x_2=2",
        goal=Optimization_Type.MAXIMIZATION,
        obj_func_coeffs=[3, 2],
        constraints_vars_coeffs=[[1, 1], [2, 1], [1, 0]],
        RHS=[4, 6, 3],
        operators=["<=", "<=", "<="],
    )

    # ── Case 2: Maximization, 3 variables, all ≤ ────────────────────────────
    run_case(
        "Maximization — all ≤  (3 variables)",
        expected="status=OPTIMAL, z=273.75",
        goal=Optimization_Type.MAXIMIZATION,
        obj_func_coeffs=[5, 4, 3],
        constraints_vars_coeffs=[
            [6, 4, 2],
            [3, 2, 5],
            [5, 6, 5],
        ],
        RHS=[240, 270, 420],
        operators=["<=", "<=", "<="],
    )

    # ── Case 3: Minimization, all ≤ ─────────────────────────────────────────
    run_case(
        "Minimization — all ≤  (origin is optimal)",
        expected="status=OPTIMAL, z=0, x_1=0, x_2=0",
        goal=Optimization_Type.MINIMIZATION,
        obj_func_coeffs=[2, 3],
        constraints_vars_coeffs=[[1, 2], [2, 1]],
        RHS=[6, 8],
        operators=["<=", "<="],
    )

    # ── Case 4: Degenerate — tie in ratio test ───────────────────────────────
    run_case(
        "Maximization — degenerate tie in ratio test",
        expected="status=OPTIMAL, z=18, x_1=0, x_2=2",
        goal=Optimization_Type.MAXIMIZATION,
        obj_func_coeffs=[3, 9],
        constraints_vars_coeffs=[[1, 4], [1, 2]],
        RHS=[8, 4],
        operators=["<=", "<="],
    )

    # ── Case 5: UNBOUNDED maximization ───────────────────────────────────────
    run_case(
        "Maximization — unbounded (no upper bound on x₁)",
        expected="status=UNBOUNDED",
        goal=Optimization_Type.MAXIMIZATION,
        obj_func_coeffs=[1, 1],
        constraints_vars_coeffs=[[-1, 1]],
        RHS=[1],
        operators=["<="],
    )

    # ── Case 6: Optimal with fractional solution ─────────────────────────────
    run_case(
        "Maximization — fractional optimal solution",
        expected="status=OPTIMAL, z=21, x_1=3, x_2=1.5",
        goal=Optimization_Type.MAXIMIZATION,
        obj_func_coeffs=[5, 4],
        constraints_vars_coeffs=[[6, 4], [1, 2]],
        RHS=[24, 6],
        operators=["<=", "<="],
    )

    # ── Case 7: Minimization — non-trivial (requires actual pivoting) ─────────
    run_case(
        "Minimization — non-trivial (requires pivoting)",
        expected="status=OPTIMAL, z=-8, x_1=0, x_2=4",
        goal=Optimization_Type.MINIMIZATION,
        obj_func_coeffs=[-1, -2],
        constraints_vars_coeffs=[[1, 1], [1, 0]],
        RHS=[4, 3],
        operators=["<=", "<="],
    )

    # ── Case 8: Single variable sanity check ─────────────────────────────────
    run_case(
        "Maximization — single variable sanity check",
        expected="status=OPTIMAL, z=35, x_1=5",
        goal=Optimization_Type.MAXIMIZATION,
        obj_func_coeffs=[7],
        constraints_vars_coeffs=[[1]],
        RHS=[5],
        operators=["<="],
    )

    # ── Case 9: Mixed constraints (requires phase 1 due to >=) ─────────────
    run_case(
        "Maximization — mixed (>= and <=)",
        expected="status=OPTIMAL, z=6, x_1=3, x_2=3",
        goal=Optimization_Type.MAXIMIZATION,
        obj_func_coeffs=[1, 1],
        constraints_vars_coeffs=[[1, 1], [1, 0], [0, 1]],
        RHS=[2, 3, 3],
        operators=[">=", "<=", "<="],
    )

    # ── Case 10: Equality constraint (phase 1) ──────────────────────────────
    run_case(
        "Maximization — equality constraint",
        expected="status=OPTIMAL, z=7, x_1=3, x_2=1",
        goal=Optimization_Type.MAXIMIZATION,
        obj_func_coeffs=[2, 1],
        constraints_vars_coeffs=[[1, 1], [1, 0], [0, 1]],
        RHS=[4, 3, 3],
        operators=["=", "<=", "<="],
    )

    # ── Case 11: Infeasible system ───────────────────────────────────────────
    run_case(
        "Maximization — infeasible constraints",
        expected="status=UNFEASIBLE",
        goal=Optimization_Type.MAXIMIZATION,
        obj_func_coeffs=[1],
        constraints_vars_coeffs=[[1], [1]],
        RHS=[3, 1],
        operators=[">=", "<="],
    )

    # ── Case 12: Redundant constraint present ────────────────────────────────
    run_case(
        "Maximization — redundant constraint",
        expected="status=OPTIMAL, z=11, x_1=3, x_2=1",
        goal=Optimization_Type.MAXIMIZATION,
        obj_func_coeffs=[3, 2],
        constraints_vars_coeffs=[[1, 1], [2, 2], [1, 0]],
        RHS=[4, 8, 3],
        operators=["<=", "<=", "<="],
    )

    # ── Case 13: Multiple optimal solutions ──────────────────────────────────
    run_case(
        "Maximization — multiple optimum points",
        expected="status=OPTIMAL, z=4 (one of many optimal corner points)",
        goal=Optimization_Type.MAXIMIZATION,
        obj_func_coeffs=[1, 1],
        constraints_vars_coeffs=[[1, 1], [1, 0], [0, 1]],
        RHS=[4, 4, 4],
        operators=["<=", "<=", "<="],
    )

    # ── Case 14: Minimization with >= and = (phase 1 + phase 2) ─────────────
    run_case(
        "Minimization — mixed >= and =",
        expected="status=OPTIMAL, z=5, x_1=2, x_2=3",
        goal=Optimization_Type.MINIMIZATION,
        obj_func_coeffs=[1, 1],
        constraints_vars_coeffs=[[1, 1], [1, 2]],
        RHS=[5, 8],
        operators=[">=", "="],
    )