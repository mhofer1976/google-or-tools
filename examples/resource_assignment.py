#!/usr/bin/env python3
# Resource Assignment Problem using OR-Tools

import numpy as np
import matplotlib.pyplot as plt
from ortools.linear_solver import pywraplp


def solve_assignment_problem():
    """Solve a resource assignment problem where we need to assign workers to
    tasks.

    The goal is to minimize the total cost while ensuring each worker is
    assigned to exactly one task and each task is assigned to exactly one
    worker.
    """
    # Create the solver
    solver = pywraplp.Solver.CreateSolver('SCIP')
    if not solver:
        print('Could not create solver SCIP')
        return

    # Problem data
    num_workers = 4
    num_tasks = 4

    # Cost matrix: cost[i][j] is the cost of assigning worker i to task j
    costs = [
        [90, 80, 75, 70],   # Worker 0 costs
        [35, 85, 55, 65],   # Worker 1 costs
        [125, 95, 90, 95],  # Worker 2 costs
        [45, 110, 95, 115]  # Worker 3 costs
    ]

    # Create variables
    # x[i][j] is 1 if worker i is assigned to task j, 0 otherwise
    x = {}
    for i in range(num_workers):
        for j in range(num_tasks):
            x[i, j] = solver.BoolVar(f'x_{i}_{j}')

    # Add constraints
    # Each worker is assigned to exactly one task
    for i in range(num_workers):
        solver.Add(solver.Sum([x[i, j] for j in range(num_tasks)]) == 1)

    # Each task is assigned to exactly one worker
    for j in range(num_tasks):
        solver.Add(solver.Sum([x[i, j] for i in range(num_workers)]) == 1)

    # Set objective: minimize total cost
    objective = solver.Objective()
    for i in range(num_workers):
        for j in range(num_tasks):
            objective.SetCoefficient(x[i, j], costs[i][j])
    objective.SetMinimization()

    # Solve the problem
    status = solver.Solve()

    # Print solution
    if status == pywraplp.Solver.OPTIMAL:
        print('Solution found!')
        print(f'Total cost = {solver.Objective().Value()}')
        print('\nAssignments:')
        for i in range(num_workers):
            for j in range(num_tasks):
                if x[i, j].solution_value() > 0.5:
                    print(f'Worker {i} -> Task {j} (Cost: {costs[i][j]})')
    else:
        print('No solution found.')

    return solver, x, costs, status


def visualize_solution(solver, x, costs, status):
    """Visualize the assignment solution using a heatmap."""
    if status != pywraplp.Solver.OPTIMAL:
        return

    num_workers = 4
    num_tasks = 4

    # Create assignment matrix
    assignment = np.zeros((num_workers, num_tasks))
    for i in range(num_workers):
        for j in range(num_tasks):
            if x[i, j].solution_value() > 0.5:
                assignment[i, j] = 1

    # Create the plot
    plt.figure(figsize=(10, 8))

    # Plot the cost matrix as a heatmap
    plt.imshow(costs, cmap='YlOrRd', aspect='auto')
    plt.colorbar(label='Cost')

    # Add text annotations for costs
    for i in range(num_workers):
        for j in range(num_tasks):
            color = 'white' if costs[i][j] > np.mean(costs) else 'black'
            plt.text(
                j, i, f'{costs[i][j]}',
                ha='center', va='center', color=color
            )

    # Highlight the assignments
    for i in range(num_workers):
        for j in range(num_tasks):
            if assignment[i, j] == 1:
                plt.gca().add_patch(
                    plt.Rectangle(
                        (j-0.5, i-0.5), 1, 1,
                        fill=False, edgecolor='green', lw=3
                    )
                )

    plt.title(
        'Resource Assignment Solution\n(Green boxes indicate assignments)'
    )
    plt.xlabel('Tasks')
    plt.ylabel('Workers')
    plt.xticks(range(num_tasks), [f'Task {i}' for i in range(num_tasks)])
    plt.yticks(range(num_workers), [f'Worker {i}' for i in range(num_workers)])
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    solver, x, costs, status = solve_assignment_problem()
    visualize_solution(solver, x, costs, status)
