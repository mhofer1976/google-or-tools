"""
Simple example using Google OR-Tools to solve a linear optimization problem.
This example finds the optimal solution for maximizing profit in a simple production scenario.
"""
from ortools.linear_solver import pywraplp

def simple_optimization_example():
    # Create the solver
    solver = pywraplp.Solver.CreateSolver('GLOP')
    
    if not solver:
        return None

    # Create variables
    x = solver.NumVar(0, float('inf'), 'x')  # Product 1
    y = solver.NumVar(0, float('inf'), 'y')  # Product 2

    # Create constraints
    # Resource 1: 2x + y ≤ 100
    solver.Add(2 * x + y <= 100)
    # Resource 2: x + 2y ≤ 100
    solver.Add(x + 2 * y <= 100)

    # Objective function: maximize 3x + 4y
    solver.Maximize(3 * x + 4 * y)

    # Solve the problem
    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        print('Solution found!')
        print(f'Optimal objective value = {solver.Objective().Value()}')
        print(f'x = {x.solution_value()}')
        print(f'y = {y.solution_value()}')
    else:
        print('No solution found.')

if __name__ == '__main__':
    simple_optimization_example()
