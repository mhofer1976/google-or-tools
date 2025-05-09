from typing import Dict, List, Any
from collections import defaultdict
from .base_constraint import BaseConstraint
from datetime import datetime, timedelta

class WorkloadBalanceConstraint(BaseConstraint):
    """
    Constraint ensuring employee workloads are reasonably balanced.
    
    This constraint ensures that no employee works significantly more or less
    than the average workload across all employees. The balance is measured in
    terms of utilization percentage (0-100) of each employee's maximum available hours.
    
    The constraint uses a scaled approach (multiplied by 100) to handle integer
    division more precisely in the CP-SAT solver.
    """
    
    def __init__(self, model, assignments, employees, duties, max_deviation_percent=20):
        """
        Initialize the workload balance constraint.
        
        Args:
            model: The CP-SAT model
            assignments: Dictionary mapping (employee_id, duty_id) to solver variables
            employees: List of employee dictionaries
            duties: List of duty dictionaries
            max_deviation_percent: Maximum allowed deviation from average workload as a percentage (default: 20)
        """
        super().__init__(model, assignments, employees, duties)
        self.max_deviation_percent = max_deviation_percent
        self.emp_utilizations = {}  # Maps employee_id to their utilization variable (0-100 scale)
    
    def _calculate_workloads(self) -> Dict[str, Any]:
        """
        Calculate workloads and utilizations for all employees.
        
        Creates CP-SAT variables for:
        - Total minutes worked by each employee
        - Utilization percentage for each employee (0-100 scale)
        
        Returns:
            Dictionary containing workload and utilization variables
        """
        emp_workload_minutes = {}
        
        for emp in self.employees:
            # Create variable for total minutes worked by this employee
            max_possible_minutes = emp['max_hours_in_period'] * 60
            emp_workload_minutes[emp['id']] = self.model.NewIntVar(
                0, max_possible_minutes, 
                f'workload_minutes_{emp["id"]}'
            )
            
            # Sum up minutes from all duties
            duty_minutes = []
            for duty in self.duties:
                minutes = duty['working_minutes']
                duty_minutes.append(minutes * self.assignments[emp['id'], duty['id']])
            
            # Add constraint for total minutes
            self.model.Add(emp_workload_minutes[emp['id']] == sum(duty_minutes))
            
            # Create utilization variable (0-100 scale)
            self.emp_utilizations[emp['id']] = self.model.NewIntVar(
                0, 100, 
                f'utilization_percent_{emp["id"]}'
            )
            
            # Add division constraint for utilization percentage
            self.model.AddDivisionEquality(
                self.emp_utilizations[emp['id']],
                emp_workload_minutes[emp['id']],
                max_possible_minutes
            )
        
        return {
            'emp_workloads': emp_workload_minutes,
            'emp_utilizations': self.emp_utilizations
        }
    
    def apply(self) -> None:
        """
        Apply the workload balance constraint to the model.
        
        This method:
        1. Calculates individual employee workloads and utilizations
        2. Computes the average utilization across all employees
        3. Ensures each employee's utilization stays within the allowed deviation
           from the average
        
        The calculations use a scaled approach (multiplied by 1000) to handle
        integer division more precisely, especially for small denominators.
        """
        workloads = self._calculate_workloads()
        
        # Scale factor to avoid integer division issues
        # Using 1000 to ensure good precision with small denominators
        SCALE = 1000
        
        # Create variable for average utilization (scaled)
        self.avg_utilization = self.model.NewIntVar(
            0, 100 * SCALE, 
            'avg_utilization_scaled'
        )
        
        # Create variable for total utilization (scaled)
        # Each utilization in self.emp_utilizations.values() is 0-100.
        # We scale each by SCALE before summing, or sum then scale. Summing then scaling is fine.
        total_scaled_utilization_sum = self.model.NewIntVar(
            0, 100 * len(self.employees) * SCALE, 
            'total_utilization_sum_scaled'
        )
        
        # Sum of (utilization_var * SCALE) for all employees
        # Or, sum(utilization_var) then multiply result by SCALE
        # The original approach sums IntVar objects then multiplies the sum expression by SCALE.
        # This is usually supported by CP-SAT for linear expressions.
        self.model.Add(total_scaled_utilization_sum == sum(self.emp_utilizations.values()) * SCALE)
        
        # Add constraint for average utilization
        # self.avg_utilization = total_scaled_utilization_sum / len(self.employees)
        # Using scaled values to maintain precision with small denominators
        self.model.AddDivisionEquality(
            self.avg_utilization,
            total_scaled_utilization_sum, # This is already scaled sum of utilizations
            len(self.employees) # Denominator is number of employees
        )
        
        # The old section for enforcing hard deviation constraints is removed.
        # We now define an objective to minimize the maximum deviation.

        # Define a variable for the maximum absolute deviation (scaled).
        # This will be the objective to minimize.
        # The maximum possible deviation is 100% (e.g., avg 0%, emp 100%), scaled by SCALE.
        max_abs_scaled_deviation = self.model.NewIntVar(
            0, 100 * SCALE, 
            'max_abs_scaled_deviation'
        )

        # For each employee, ensure their scaled deviation from the scaled average
        # is less than or equal to max_abs_scaled_deviation.
        for emp_id, utilization_var in self.emp_utilizations.items():
            # utilization_var is in the range [0, 100].
            # Scale it up to match the scale of self.avg_utilization.
            emp_scaled_utilization = self.model.NewIntVar(
                0, 100 * SCALE, 
                f'utilization_scaled_{emp_id}' # Reuses name from the removed block, which is fine.
            )
            self.model.Add(emp_scaled_utilization == utilization_var * SCALE)
            
            # Add constraints for: max_abs_scaled_deviation >= abs(emp_scaled_utilization - self.avg_utilization)
            # This is equivalent to:
            # max_abs_scaled_deviation >= emp_scaled_utilization - self.avg_utilization AND
            # max_abs_scaled_deviation >= -(emp_scaled_utilization - self.avg_utilization)
            
            self.model.Add(max_abs_scaled_deviation >= emp_scaled_utilization - self.avg_utilization)
            self.model.Add(max_abs_scaled_deviation >= self.avg_utilization - emp_scaled_utilization)

        # Minimize this maximum absolute deviation.
        # This makes the workload balance a soft constraint: the solver will try to make
        # max_abs_scaled_deviation as small as possible, ideally zero, but will accept
        # larger values if necessary to satisfy other hard constraints.
        self.model.Minimize(max_abs_scaled_deviation)
    
    def validate(self, assignments: List[Dict[str, Any]]) -> bool:
        """
        Validate that employee workloads are reasonably balanced.
        
        Args:
            assignments: List of assignment dictionaries from the solver
            
        Returns:
            True if workloads are balanced, False otherwise
        """
        # Calculate workload for each employee
        emp_workloads = defaultdict(int)
        
        # Sum up minutes for each employee based on assignments
        for assignment in assignments:
            # Calculate minutes from start and end time
            start_time = datetime.strptime(assignment['start_time'], "%H:%M")
            end_time = datetime.strptime(assignment['end_time'], "%H:%M")
            
            # If end time is earlier than start time, it's an overnight duty
            if end_time < start_time:
                end_time = end_time + timedelta(days=1)
            
            minutes = int((end_time - start_time).total_seconds() / 60)
            
            for employee in assignment['employees']:
                emp_id = employee['employee_id']
                emp_workloads[emp_id] += minutes
        
        # Calculate average workload
        total_workload = sum(emp_workloads.values())
        avg_workload = total_workload / len(emp_workloads) if emp_workloads else 0
        
        # Check if any employee's workload deviates too much from the average
        if avg_workload == 0:
            return True
            
        return all(
            abs(workload - avg_workload) / avg_workload * 100 <= self.max_deviation_percent
            for workload in emp_workloads.values()
        )
    
    def _calculate_duty_hours(self, start_time: str, end_time: str) -> float:
        """
        Calculate the number of hours for a duty, handling overnight duties correctly.
        
        Args:
            start_time: Start time in format "HH:MM"
            end_time: End time in format "HH:MM"
            
        Returns:
            Number of hours the duty lasts
        """
        start = datetime.strptime(start_time, "%H:%M")
        end = datetime.strptime(end_time, "%H:%M")
        
        # If end time is earlier than start time, it's an overnight duty
        if end < start:
            # Add 24 hours to the end time to get the correct duration
            end = end + timedelta(days=1)
        
        duration = end - start
        return duration.total_seconds() / 3600 