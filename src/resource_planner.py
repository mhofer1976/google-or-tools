from ortools.sat.python import cp_model
from datetime import datetime, timedelta, date
from typing import List, Dict, Set, Tuple, Optional, Type

from .constraints import (
    BaseConstraint,
    RequiredEmployeesConstraint,
    BlockedDaysConstraint,
    OneDutyPerDayConstraint,
    RestTimeConstraint,
    MaxDaysInARowConstraint,
    WorkloadBalanceConstraint,
)

class ResourcePlanner:
    """
    A constraint-based resource planner that uses OR-Tools to solve employee scheduling problems.
    
    This planner allows adding various constraints to ensure the schedule meets all requirements.
    """
    
    def __init__(self):
        """Initialize the resource planner with an empty model and data structures."""
        self.model = cp_model.CpModel()
        self.assignments = {}
        self.employees = []
        self.duties = []
        self.calendar_days = set()
        self.constraints = []
        
    def add_employee(self, id: int, name: str, max_days_in_row: int, 
                    blocked_days: List[str], max_hours_per_day: int,
                    max_hours_in_period: int, work_percentage: int) -> None:
        """
        Add an employee to the planning system.
        
        Args:
            id: Unique identifier for the employee
            name: Employee's name
            max_days_in_row: Maximum number of consecutive days the employee can work
            blocked_days: List of dates (YYYY-MM-DD) when the employee cannot work
            max_hours_per_day: Maximum hours the employee can work in a day
            max_hours_in_period: Maximum hours the employee can work in the planning period
            work_percentage: Employee's work percentage (0-100)
        """
        self.employees.append({
            "id": id,
            "name": name,
            "max_days_in_a_row": max_days_in_row,
            "blocked_days": blocked_days,
            "max_hours_per_day": max_hours_per_day,
            "max_hours_in_period": max_hours_in_period,
            "work_percentage": work_percentage,
        })
        
    def add_duty(self, code: str, required_employees: int, start_time: str, end_time: str) -> int:
        """
        Add a duty/shift to the planning system.
        
        Args:
            code: Duty code (e.g., "DIS", "OPS")
            required_employees: Number of employees required for this duty
            start_time: Start time in format "HH:MM"
            end_time: End time in format "HH:MM"
            
        Returns:
            The ID of the newly created duty
        """
        duty_id = len(self.duties)
        duty = {
            "id": duty_id,
            "code": code,
            "required_employees": required_employees,
            "start_time": start_time,
            "end_time": end_time,
            "date": None,  # Will be set when expanding duties
        }
        self.duties.append(duty)
        return duty_id
        
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
        
    def solve(self):
        """
        Solve the resource planning problem.
        
        Returns:
            List of assignment dictionaries with the following fields:
            - date: The date of the assignment
            - employee_id: The ID of the assigned employee
            - duty_id: The ID of the assigned duty
            - duty_code: The code of the assigned duty
            - start_time: The start time of the duty
            - end_time: The end time of the duty
            - employee_name: The name of the assigned employee
        """
        solver = cp_model.CpSolver()
        status = solver.Solve(self.model)
        
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            assignments = []
            
            # Process the solution
            for emp in self.employees:
                for duty in self.duties:
                    if solver.Value(self.assignments[emp['id'], duty['id']]) == 1:
                        # Create an assignment with all necessary fields
                        assignment = {
                            "date": duty['date'],
                            "employee_id": emp['id'],
                            "duty_id": duty['id'],
                            "duty_code": duty['code'],
                            "start_time": duty['start_time'],
                            "end_time": duty['end_time'],
                            "employee_name": emp['name']
                        }
                        assignments.append(assignment)
            
            return assignments
        
        return []
        
    def validate_solution(self, solution):
        """
        Validate a solution against all constraints.
        
        Args:
            solution: List of assignment dictionaries
            
        Returns:
            Dictionary mapping constraint names to validation results (True/False)
        """
        validation_results = {}
        
        for constraint in self.constraints:
            constraint_name = constraint.__class__.__name__
            is_valid = constraint.validate(solution)
            validation_results[constraint_name] = is_valid
            
        return validation_results 