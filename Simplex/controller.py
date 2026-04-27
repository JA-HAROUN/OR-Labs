from fastapi import FastAPI
from pydantic import BaseModel
import asyncio

from Simplex import Simplex

class InputData(BaseModel):
    goal: str
    objective_coefficients: list[float]
    constraints_coefficients: list[list[float]]
    constraints_rhs: list[float]
    operators: list[str]

class Solution(BaseModel):
    last_tableau_data: {} | None = None
    iteration_history: {} | None = None
    # simplex properties
    basic_variables: list[int] | None = None
    non_basic_variables: list[int] | None = None
    degenerate_count: int | None = None
    slack_nums: int | None = None
    surplus_nums: int | None = None
    artificial_nums: int | None = None
    unbounded: bool | None = None

app = FastAPI()

@app.post("/solve")
async def solve(input_data: InputData):
    # Create an instance of the Simplex class and solve the problem
    simplex = Simplex(
        goal=input_data.goal,
        objective_coefficients=input_data.objective_coefficients,
        constraints_coefficients=input_data.constraints_coefficients,
        constraints_rhs=input_data.constraints_rhs,
        operators=input_data.operators
    )
    
    simplex.run_program()
    
    # Prepare the solution data to return as JSON
    solution = Solution(
        last_tableau_data=simplex.last_tableau_data,
        iteration_history=simplex.iteration_history,
        basic_variables=simplex.basic_variables,
        non_basic_variables=simplex.non_basic_variables,
        degenerate_count=simplex.degenerate_count,
        slack_nums=simplex.slack_nums,
        surplus_nums=simplex.surplus_nums,
        artificial_nums=simplex.artificial_nums,
        unbounded=simplex.unbounded
    )
    
    return solution
    
    