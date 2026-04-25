from enum import Enum
import math
import numpy as np

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
    FREE = 2

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
    
    def __init__(self, goal=Optimization_Type.NULL, obj_func_coeffs=(), constraints_vars_coeffs=(), RHS=(), operators=()):
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
        
        self.goal = goal
        
        # -c1   -c2     -c3 .....   result(0 in the beginning but changes with pivoting)
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
    
    
    # Behaviours
    # *** Normal Simplex ***
    """
        Steps:
            1. if pivot value != 1 divide the row with its value
            2. u = element in different row / pivot
            3. (the pivot row * -u ) + that different row from step 2
            4. do step 2 and 3 for all constraints_vars_coeffs rows
                NOTE: include the RHS in it
            5. last thing do the same for the objective function
    """
        
    # DONE: Implement the pivoting operation
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
        
    
    # DONE: Implement the ratio test to find the leaving variable
    def ratio_test(self, column_index):
        row = -1
        min_ratio = float('inf')
        degenerate = False

        for i, rhs_value in enumerate(self.RHS):
            divisor = self.constraints_vars_coeffs[i][column_index]
            
            if divisor > 0:
                current_ratio = rhs_value / divisor
                
                if current_ratio < min_ratio:
                    min_ratio = current_ratio
                    row = i
                    degenerate = False  # Reset if we find a new unique minimum
                
                elif current_ratio == min_ratio:
                    # We have a tie for the minimum ratio
                    degenerate = True

        if degenerate:
            self.degenerate_count += 1
            # NOTE: would use Bland's Rule here 
            # (choosing the smallest index) to prevent infinite loops.

        return row
    
    # DONE: Check if the goal is achieved or not
    def goal_achieved(self):
        # Return True or False based on achieved or not
        # if Maximization:
        #   Check if all obj_func_coeffs are non-negative
        # else:
        #   Check if all obj_func_coeffs are non_positive
        if (self.goal == Optimization_Type.MAXIMIZATION):
            return bool(np.all(self.obj_func_coeffs >= 0))
        elif (self.goal == Optimization_Type.MINIMIZATION):
            return bool(np.all(self.obj_func_coeffs <= 0))

        return True
    
    # DONE: Choose entering variable
    def choose_entering_var(self):
        # Maximization -> Most Negative
        # Minimization -> Most Positive
        # NOTE: if there are equal values take the left most (best practice)
        # NOTE: if artificial_variable ignore it
        
        entering_var_index = -1
        
        if (self.goal == Optimization_Type.MAXIMIZATION):
            negative_indices = np.where(self.obj_func_coeffs < 0)[0]
            if negative_indices.size > 0:
                entering_var_index = int(negative_indices[np.argmin(self.obj_func_coeffs[negative_indices])])
            else:
                self.finished = True

        elif (self.goal == Optimization_Type.MINIMIZATION):
            positive_indices = np.where(self.obj_func_coeffs > 0)[0]
            if positive_indices.size > 0:
                entering_var_index = int(positive_indices[np.argmax(self.obj_func_coeffs[positive_indices])])
            else:
                self.finished = True
                    
        return entering_var_index
    
    # DONE: add slack, surplus and artificial variables when needed in the start
    def add_variables(self):
        for i, _ in enumerate(self.constraints_vars_coeffs) :
            operator = self.operators[i]
            if operator == "<=":
                # add slack
                self.slacks_num += 1
                new_slack = f"s_{self.slacks_num}"
                self.basic_vars.append(new_slack)
                self.variables.append(new_slack)
                self.obj_func_coeffs = np.append(self.obj_func_coeffs, 0.0)

            elif operator == ">=":
                # add surplus
                self.surplus_num += 1
                new_surplus = f"e_{self.surplus_num}"
                self.basic_vars.append(new_surplus)
                self.variables.append(new_surplus)
                self.obj_func_coeffs = np.append(self.obj_func_coeffs, 0.0)

            elif operator == "=":
                # add artificial variables
                self.artificial_num += 1
                new_artificial = f"a_{self.artificial_num}"
                self.basic_vars.append(new_artificial)
                self.variables.append(new_artificial)
                self.obj_func_coeffs = np.append(self.obj_func_coeffs, 0.0)
            else :
                raise ValueError(f"Unsupported operator: {operator}")

            # add column
            new_column = np.zeros((self.num_of_constraints, 1), dtype=float)
            new_column[i, 0] = 1.0

            self.constraints_vars_coeffs = np.hstack((self.constraints_vars_coeffs, new_column))
            
    
    # DONE: Implement the first phase of the two-phase method
    def run_phase_one(self):

        self.phase_one_flag = True

        old_objective_coeffs = self.obj_func_coeffs
        old_goal = self.goal

        new_objective_coeffs = np.ones(self.artificial_num, dtype=float)
        new_goal = Optimization_Type.MINIMIZATION

        self.obj_func_coeffs = new_objective_coeffs
        self.goal = new_goal

        self.obj_func_coeffs = -self.obj_func_coeffs

        # make rows in objective under the artificial variables zero
        for i in range(self.num_of_constraints):
            if self.basic_vars[i].startswith("a_"):
                # as down is zero and up is 1 then add the row to the objective function
                self.obj_func_coeffs = self.obj_func_coeffs + self.constraints_vars_coeffs[i]
                self.output = self.output + self.RHS[i]

        # AI_GENERATED: This part is AI generated
        print("\n" + "═" * 60)
        print("  PHASE 1  —  Minimize artificial variables  (W → 0)")
        print("═" * 60)
        self.print_solution(False)

        # AI_GENERATED: This part is AI generated
        iteration = 0
        # Run the simplex algorithm for phase one
        while (not self.goal_achieved()):
            iteration += 1
            entering_var_index = self.choose_entering_var()
            
            if self.finished:
                break

            # capture names before swapping
            entering_var_name = self.variables[entering_var_index]
            leaving_var_row   = self.ratio_test(entering_var_index)
            leaving_var_name  = self.basic_vars[leaving_var_row]

            # if ratio_test found no positive element → unbounded (no leaving var)
            if leaving_var_row == -1:
                self.unbounded = True
                break

            # swap entering with leaving
            self.basic_vars[leaving_var_row] = entering_var_name

            self.pivoting(leaving_var_row, entering_var_index)

            # AI_GENERATED: This part is AI generated
            print(f"  ▶  Phase 1 | Iteration {iteration}")
            print(f"     Entering : {entering_var_name}   →   Leaving : {leaving_var_name}")
            self.print_solution(False)

        # Check the result of phase one
        self.check_failure()
        if self.solution == Simplex_Solution.UNFEASIBLE:
            return

        self.phase_one_flag = False
        self.obj_func_coeffs = old_objective_coeffs
        self.goal = old_goal
        self.output = np.array([0.0], dtype=float)
        
    def run_phase_two(self):
        # NOTE: in phase two we just ignore the artificial variables and never let them enter the basis again

        # AI_GENERATED: This part is AI generated
        print("\n" + "═" * 60)
        print("  PHASE 2  —  Optimize original objective")
        print("═" * 60)
        self.print_solution(False)

        iteration = 0
        while (not self.goal_achieved()):
            iteration += 1
            entering_var_index = self.choose_entering_var()
            
            if self.finished:
                break

            # capture names before swapping
            entering_var_name = self.variables[entering_var_index]
            leaving_var_row   = self.ratio_test(entering_var_index)
            leaving_var_name  = self.basic_vars[leaving_var_row]

            # if ratio_test found no positive element → unbounded
            if leaving_var_row == -1:
                self.unbounded = True
                break

            # swap entering with leaving
            self.basic_vars[leaving_var_row] = entering_var_name

            self.pivoting(leaving_var_row, entering_var_index)

            # AI_GENERATED: This part is AI generated
            print(f"  ▶  Phase 2 | Iteration {iteration}")
            print(f"     Entering : {entering_var_name}   →   Leaving : {leaving_var_name}")
            self.print_solution(False)  
            
        # Check the result of phase two
        self.check_failure()
        
    
    # DONE: Implement the main method to run the simplex algorithm
    def run_program(self):
        self.obj_func_coeffs = -self.obj_func_coeffs

        self.add_variables()

        # AI_GENERATED: This part is AI generated
        print("\n" + "═" * 60)
        print("  INITIAL TABLEAU  —  After adding auxiliary variables")
        print("═" * 60)
        self.print_solution(False)

        # Check phase 1 if there are artificial variables
        if self.artificial_num >= 1:
            # NOTE: before it save the old objective function variables, and type
            result = self.run_phase_one()
            if (self.solution == Simplex_Solution.UNFEASIBLE):
                # AI_GENERATED: This part is AI generated
                print("\n  ✘  UNFEASIBLE  —  No feasible solution exists.\n")
                return

        # Do phase 2 if phase 1 was okay
        self.run_phase_two()

        # AI_GENERATED: This part is AI generated
        print("\n" + "═" * 60)
        print("  RESULT")
        print("═" * 60)

        if self.solution == Simplex_Solution.OPTIMAL:
            self.print_solution(True)
        elif self.solution == Simplex_Solution.UNBOUNDED:
            print("  ∞  UNBOUNDED  —  The objective has no finite optimum.\n")
        elif self.solution == Simplex_Solution.UNFEASIBLE:
            print("  ✘  UNFEASIBLE  —  No feasible solution exists.\n")
        else:
            # fallback: print whatever state we ended in
            self.print_solution(True)
    
    # DONE: Check for unboundedness and infeasibility after each phase
    def check_failure(self):
        if (self.goal == Optimization_Type.MINIMIZATION and self.phase_one_flag):
            if self.output != 0 and np.all(self.obj_func_coeffs >= 0):
                self.solution = Simplex_Solution.UNFEASIBLE
                return

        if self.unbounded:
            self.solution = Simplex_Solution.UNBOUNDED
            return

        if self.finished or self.goal_achieved():
            self.solution = Simplex_Solution.OPTIMAL
        
        
    # AI_GENERATED: This part is AI generated
    def print_solution(self, finished):
        # ── column headers ────────────────────────────────────────────────────
        # self.variables is always in sync with tableau columns (original + slack/surplus/artificial)
        total_vars = len(self.obj_func_coeffs)
        col_names  = self.variables[:total_vars]

        # ── column widths ─────────────────────────────────────────────────────
        COL_W = 9   # width for each variable column
        BV_W  = 7   # width for the BV label column
        RHS_W = 9   # width for the RHS column

        def fmt(val):
            """Format a float nicely — integer when possible."""
            if val == int(val):
                return str(int(val))
            return f"{val:.4g}"

        def cell(text, width):
            return str(text).center(width)

        # ── border strings ────────────────────────────────────────────────────
        inner_w = BV_W + total_vars * (COL_W + 1) + RHS_W + 2
        top = "┌" + "─" * inner_w + "┐"
        mid = "├" + "─" * inner_w + "┤"
        bot = "└" + "─" * inner_w + "┘"

        def row_str(bv, coeffs, rhs):
            line = "│ " + cell(bv, BV_W) + " │"
            for c in coeffs:
                line += cell(fmt(c), COL_W) + " "
            line += "│ " + cell(fmt(rhs), RHS_W - 1) + "│"
            return line

        def header_str():
            line = "│ " + cell("BV", BV_W) + " │"
            for name in col_names:
                line += cell(name, COL_W) + " "
            line += "│ " + cell("RHS", RHS_W - 1) + "│"
            return line

        # ── render ────────────────────────────────────────────────────────────
        label = "✔  Optimal Solution" if finished else "⟳  Current Tableau"
        print(f"\n  {label}")
        print(top)
        print(header_str())
        print(mid)

        for i, bv in enumerate(self.basic_vars):
            print(row_str(bv, self.constraints_vars_coeffs[i], self.RHS[i]))

        print(mid)

        # z-row: self.output holds the current objective value directly (positive)
        z_val = float(self.output[0]) if hasattr(self.output, "__len__") else float(self.output)
        print(row_str("z", self.obj_func_coeffs, z_val))

        print(bot)

        if finished:
            print(f"  Optimal value             : {fmt(z_val)}")
            print(f"  Degenerate pivots found   : {self.degenerate_count}")
        print()
        
    
    # *** Two Phase ***
    """
        Sequence:
            1. add artificial variables as much as operators of = or >=
                NOTE: >= give Surplus variables but they are negative
                but multiplying by -1 makes the RHS negative so adding artificial variables is better
                TODO: Think about it again
            2. new Objective Function -> Minimize W = Summation of (a_i)
                a_i : artifical variable i
            3. Check Minimization Result
                1- W = 0 -> Success
                2- W != 0 and no way to do it -> No Feasible Solution for the Problem
                
            4. In case it succeeded then get back to the normal phase 2
                NOTE: Never use the artificial variable do calculations in it 
                      but never enter it again
    """
    
    
    
    
    pass


if __name__ == "__main__":

    # AI_GENERATED: This part is AI generated
    def run_case(title, **kwargs):
        """Helper — prints a banner then runs one simplex instance."""
        print("\n" + "█" * 60)
        print(f"  TEST CASE : {title}")
        print("█" * 60)
        s = Simplex(**kwargs)
        s.run_program()

    # AI_GENERATED: This part is AI generated
    # ── Case 1: Maximization, all ≤ (Hamdy Taha classic) ────────────────────
    # max  z = 3x₁ + 2x₂
    # s.t.  x₁ +  x₂ ≤ 4
    #       2x₁ + x₂ ≤ 6
    #       x₁       ≤ 3
    # Expected optimal: z = 10  (x₁=2, x₂=2)  — no degeneracy
    run_case(
        "Maximization — all ≤  (3×2, Hamdy Taha)",
        goal=Optimization_Type.MAXIMIZATION,
        obj_func_coeffs=[3, 2],
        constraints_vars_coeffs=[[1, 1], [2, 1], [1, 0]],
        RHS=[4, 6, 3],
        operators=["<=", "<=", "<="],
    )

    # AI_GENERATED: This part is AI generated
    # ── Case 2: Maximization, 3 variables, all ≤ ────────────────────────────
    # max  z = 5x₁ + 4x₂ + 3x₃
    # s.t.  6x₁ + 4x₂ + 2x₃ ≤ 240
    #       3x₁ + 2x₂ + 5x₃ ≤ 270
    #       5x₁ + 6x₂ + 5x₃ ≤ 420
    # Expected optimal: z = 305
    run_case(
        "Maximization — all ≤  (3 variables)",
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

    # AI_GENERATED: This part is AI generated
    # ── Case 3: Minimization, all ≤ ─────────────────────────────────────────
    # min  z = 2x₁ + 3x₂
    # s.t.  x₁ + 2x₂ ≤ 6
    #       2x₁ +  x₂ ≤ 8
    # Expected optimal: z = 0  (trivial, origin is feasible for minimization)
    # (demonstrates that simplex correctly detects the origin as optimal
    #  when all original variable coefficients in z are non-negative
    #  and the constraints are ≤ type)
    run_case(
        "Minimization — all ≤  (origin is optimal)",
        goal=Optimization_Type.MINIMIZATION,
        obj_func_coeffs=[2, 3],
        constraints_vars_coeffs=[[1, 2], [2, 1]],
        RHS=[6, 8],
        operators=["<=", "<="],
    )

    # AI_GENERATED: This part is AI generated
    # ── Case 4: Degenerate — tie in ratio test ───────────────────────────────
    # max  z = 3x₁ + 9x₂
    # s.t.   x₁ + 4x₂ ≤ 8     ← both rows give ratio = 2, causing degeneracy
    #        x₁ + 2x₂ ≤ 4
    # Expected: OPTIMAL  z = 18  (x₁=0, x₂=2)
    run_case(
        "Maximization — degenerate tie in ratio test",
        goal=Optimization_Type.MAXIMIZATION,
        obj_func_coeffs=[3, 9],
        constraints_vars_coeffs=[[1, 4], [1, 2]],
        RHS=[8, 4],
        operators=["<=", "<="],
    )

    # AI_GENERATED: This part is AI generated
    # ── Case 5: UNBOUNDED maximization ───────────────────────────────────────
    # max  z = x₁ + x₂
    # s.t.  -x₁ + x₂ ≤ 1          ← no upper bound on x₁ direction
    #        x₁       ≤  ∞  (missing)
    # The column of x₁ has only non-positive constraint coefficients,
    # so ratio_test returns -1 → problem is unbounded.
    # Expected: UNBOUNDED
    run_case(
        "Maximization — unbounded (no upper bound on x₁)",
        goal=Optimization_Type.MAXIMIZATION,
        obj_func_coeffs=[1, 1],
        constraints_vars_coeffs=[[-1, 1]],
        RHS=[1],
        operators=["<="],
    )

    # AI_GENERATED: This part is AI generated
    # ── Case 6: Optimal with fractional solution ─────────────────────────────
    # max  z = 5x₁ + 4x₂
    # s.t.  6x₁ +  4x₂ ≤ 24
    #        x₁ +  2x₂ ≤  6
    # Expected: OPTIMAL  z = 21  (x₁=3, x₂=3/2)
    #   Verify: 5(3) + 4(1.5) = 15 + 6 = 21  ✓
    run_case(
        "Maximization — fractional optimal solution",
        goal=Optimization_Type.MAXIMIZATION,
        obj_func_coeffs=[5, 4],
        constraints_vars_coeffs=[[6, 4], [1, 2]],
        RHS=[24, 6],
        operators=["<=", "<="],
    )

    # AI_GENERATED: This part is AI generated
    # ── Case 7: Minimization — non-trivial (requires actual pivoting) ─────────
    # min  z = -x₁ - 2x₂            ← negating forces algorithm to pivot
    # s.t.  x₁ + x₂ ≤ 4
    #       x₁      ≤ 3
    # After negation in run_program: internal coeffs become [1, 2, ...]
    # The minimization loop picks the most-positive coefficient and pivots.
    # Expected: OPTIMAL  z = -7  (x₁=1, x₂=3)
    run_case(
        "Minimization — non-trivial (requires pivoting)",
        goal=Optimization_Type.MINIMIZATION,
        obj_func_coeffs=[-1, -2],
        constraints_vars_coeffs=[[1, 1], [1, 0]],
        RHS=[4, 3],
        operators=["<=", "<="],
    )

    # AI_GENERATED: This part is AI generated
    # ── Case 8: Single variable sanity check ─────────────────────────────────
    # max  z = 7x₁
    # s.t.  x₁ ≤ 5
    # Expected: OPTIMAL  z = 35  (x₁=5)
    run_case(
        "Maximization — single variable sanity check",
        goal=Optimization_Type.MAXIMIZATION,
        obj_func_coeffs=[7],
        constraints_vars_coeffs=[[1]],
        RHS=[5],
        operators=["<="],
    )