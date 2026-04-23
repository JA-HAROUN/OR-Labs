from enum import Enum

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
    OPTIMAL = 1
    UNBOUNDED = 2
    UNFEASIBLE = 3

class Simplex:
    
    # TODO: make the constructor as you wish
    def __init__(self, optimization_type, ):
        pass
    
    
    # States
    num_of_constraints = 0
    num_of_variables = 0
    
    goal = Optimization_Type.NULL
    
    # -c1   -c2     -c3 .....   result(0 in the beginning but changes with pivoting)
    obj_func_coeffs = []
    output = []     # has just one value
    variables = []  # x1, x2, x3, ...
    constraints_vars_coeffs = [[]]
    RHS = []
    operators = []
    
    basic_vars = []
    non_basic_vars = []
    
    # NOTE: multiply the obj_func_coeffs by -1 in the start of the solution
    
    
    # Behaviours
    # *** Normal Simplex ***
    # TODO
    def pivoting(element_x, element_y):
        """
        Steps:
            1. if pivot value != 1 divide the row with its value
            2. u = element in different row / pivot
            3. (the pivot row * -u ) + that different row from step 2
            4. do step 2 and 3 for all constraints_vars_coeffs rows
                NOTE: include the RHS in it
            5. last thing do the same for the objective function
        """
        pass
    
    # TODO: Chooses leaving variable
    def ratio_test(column_index):
        # divide RHS[i] over column[i]
        # get the min non negative ratio 
        # NOTE: Watch out for Degenracy
        # return the index from it to use in pivoting
        pass
    
    # TODO
    def goal_achieved():
        # Return True or False based on achieved or not
        # if Maximization:
        #   Check if all obj_func_coeffs are non-negative
        # else:
        #   Check if all obj_func_coeffs are non_positive
        pass
    
    # TODO
    def choose_entering_var():
        # Maximization -> Most Negative
        # Minimization -> Most Positive
        # NOTE: if there are equal values take the left most (best practice)
        # NOTE: if artificial_variable ignore it
        pass
    
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