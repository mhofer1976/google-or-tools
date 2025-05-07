from ortools.sat.python import cp_model
from datetime import datetime, timedelta, date
from typing import List, Dict, Set, Tuple, Optional, Type
import logging
import json
from pathlib import Path
from enum import Enum

from .constraints import (
    BaseConstraint,
    RequiredEmployeesConstraint,
    BlockedDaysConstraint,
    OneDutyPerDayConstraint,
    RestTimeConstraint,
    MaxDaysInARowConstraint,
    WorkloadBalanceConstraint,
)


class SolverStatus(Enum):
    """Enum representing the possible statuses of the constraint solver.
    FEASIBLE: The solver found a feasible but possibly not optimal solution"""

    OPTIMAL = "OPTIMAL"  # The solver found an optimal solution
    FEASIBLE = (
        "FEASIBLE"  # The solver found a feasible but possibly not optimal solution
    )
    INFEASIBLE = "INFEASIBLE"  # The solver determined that no feasible solution exists


class ResourcePlanner:
    """
    A constraint-based resource planner that uses OR-Tools to solve employee scheduling problems.
    
    This planner allows adding various constraints to ensure the schedule meets all requirements.
    """
    
    def __init__(self, debug_mode: bool = False, log_file: str = None):
        """
        Initialize the resource planner with an empty model and data structures.
        
        Args:
            debug_mode: Whether to enable debugging features
            log_file: Path to log file for debugging output
        """
        self.model = cp_model.CpModel()
        self.assignments = {}
        self.employees = []
        self.duties = []
        self.calendar_days = set()
        self.constraints = []
        
    def add_employee(self, id: int, name: str, max_days_in_row: int, 
                    blocked_days: List[str], max_hours_per_day: int,
                    max_hours_in_period: int) -> None:
        """
        Add an employee to the planning system.
        
        Args:
            id: Unique identifier for the employee
            name: Employee's name
            max_days_in_row: Maximum number of consecutive days the employee can work
            blocked_days: List of dates (YYYY-MM-DD) when the employee cannot work
            max_hours_per_day: Maximum hours the employee can work in a day
            max_hours_in_period: Maximum hours the employee can work in the planning period
        """
        self.employees.append({
            "id": id,
            "name": name,
            "max_days_in_a_row": max_days_in_row,
            "blocked_days": blocked_days,
            "max_hours_per_day": max_hours_per_day,
            "max_hours_in_period": max_hours_in_period
        })
        
    def add_duty(self, id: int, code: str, date: str, required_employees: int, start_time: str, end_time: str, working_minutes: int) -> None:
        """
        Add a duty/shift to the planning system.
        
        Args:
            id: Unique identifier for the duty
            code: Duty code (e.g., "DIS", "OPS")
            date: Date in format "YYYY-MM-DD"
            required_employees: Number of employees required for this duty
            start_time: Start time in format "HH:MM"
            end_time: End time in format "HH:MM"
            working_minutes: Number of minutes the duty lasts
        """
        duty = {
            "id": id,
            "code": code,
            "date": date,
            "required_employees": required_employees,
            "start_time": start_time,
            "end_time": end_time,
            "working_minutes": working_minutes
        }
        self.duties.append(duty)
        
    def add_constraint(self, constraint_class: Type[BaseConstraint], **kwargs) -> None:
        """
        Add a constraint to the planning system.
        
        Args:
            constraint_class: The constraint class to instantiate
            **kwargs: Additional arguments to pass to the constraint constructor
        """
        constraint = constraint_class(self.model, self.assignments, self.employees, self.duties, **kwargs)
        self.constraints.append(constraint)
        
    def setup_model(self) -> None:
        """
        Initialize the constraint model with all necessary variables and constraints.
        
        This method creates the assignment variables and applies all constraints.
        """
        # Create assignment variables
        for emp in self.employees:
            for duty in self.duties:
                var_name = f'emp_{emp["id"]}_duty_{duty["id"]}'
                self.assignments[emp['id'], duty['id']] = self.model.NewBoolVar(var_name)
        
        # Apply all constraints
        for constraint in self.constraints:
            constraint.apply()
        
    def solve(self) -> SolverStatus:
        """
        Solve the resource planning problem.
        
        Returns:
            SolverStatus: The status of the solver (OPTIMAL, FEASIBLE, or INFEASIBLE)
        """
        solver = cp_model.CpSolver()
        
        # Set solver parameters to help find solutions
        #TODO: make this configurable
        solver.parameters.max_time_in_seconds = 30.0  # Give the solver more time
        solver.parameters.num_search_workers = 8  # Use multiple workers
        solver.parameters.search_branching = cp_model.PORTFOLIO_SEARCH  # Use portfolio search
        solver.parameters.random_seed = 42  # Use a fixed seed for reproducibility
        
        status = solver.Solve(self.model)
        
        assignments = []
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            # Process the solution
            assignments.extend([
                {
                    "duty_id": duty['id'],
                    "duty_code": duty['code'],
                    "date": duty['date'],
                    "start_time": duty['start_time'],
                    "end_time": duty['end_time'],
                    "employees": [
                        {"employee_id": emp['id'], "employee_name": emp['name']}
                        for emp in self.employees
                        if solver.Value(self.assignments[emp['id'], duty['id']]) == 1
                    ]
                }
                for duty in self.duties
                if any(solver.Value(self.assignments[emp['id'], duty['id']]) == 1 
                      for emp in self.employees)
            ])
            
            # Sort assignments by multiple fields: date, start_time, and employee_name
            assignments.sort(key=lambda x: (x['date'], x['duty_code'], x['start_time']))
        
        self.assignments = assignments
        
        # Map OR-Tools status to our SolverStatus enum
        if status == cp_model.OPTIMAL:
            return SolverStatus.OPTIMAL
        elif status == cp_model.FEASIBLE:
            return SolverStatus.FEASIBLE
        else:
            return SolverStatus.INFEASIBLE
        
    def validate_solution(self):
        """
        Validate the current assignments against all constraints.
        
        Returns:
            Dictionary mapping constraint names to validation results (True/False)
            
        Raises:
            ValueError: If there are no valid assignments to validate
        """
        if not self.assignments:
            raise ValueError("No valid assignments to validate")
            
        validation_results = {}
        
        for constraint in self.constraints:
            constraint_name = constraint.__class__.__name__
            is_valid = constraint.validate(self.assignments)
            validation_results[constraint_name] = is_valid
            
        return validation_results
