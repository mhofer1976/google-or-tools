from typing import Dict, List, Any
from collections import defaultdict
from .base_constraint import BaseConstraint

class WorkloadBalanceConstraint(BaseConstraint):
    """
    Constraint ensuring employee workloads are reasonably balanced.
    
    This constraint ensures that no employee works significantly more or less
    than the average workload across all employees.
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
    
    def _calculate_workloads(self) -> Dict[str, Any]:
        """Calculate workloads and average for all employees."""
        # Calculate total minutes for each employee
        emp_workloads = defaultdict(int)
        total_minutes = 0
        
        for duty in self.duties:
            minutes = duty['working_minutes']
            total_minutes += minutes * duty['required_employees']
            
            for emp in self.employees:
                emp_workloads[emp['id']] += minutes * self.assignments[emp['id'], duty['id']]
        
        avg_workload = total_minutes / len(self.employees) if self.employees else 0
        
        return {
            'emp_workloads': emp_workloads,
            'total_minutes': total_minutes,
            'avg_workload': avg_workload
        }
    
    def apply(self) -> None:
        """
        Apply the workload balance constraint to the model.
        
        This adds constraints to ensure that each employee's workload is within
        the allowed deviation from the average workload.
        """
        workloads = self._calculate_workloads()
        avg_workload = workloads['avg_workload']
        
        # Calculate allowed workload range
        max_allowed = int(avg_workload * (1 + self.max_deviation_percent / 100))
        min_allowed = int(avg_workload * (1 - self.max_deviation_percent / 100))
        
        # Add constraints for each employee
        for emp_id, workload in workloads['emp_workloads'].items():
            self.model.Add(workload <= max_allowed)
            self.model.Add(workload >= min_allowed)
        
        # Add objective to minimize the maximum workload difference
        max_workload = self.model.NewIntVar(0, workloads['total_minutes'], 'max_workload')
        min_workload = self.model.NewIntVar(0, workloads['total_minutes'], 'min_workload')
        
        for workload in workloads['emp_workloads'].values():
            self.model.Add(max_workload >= workload)
            self.model.Add(min_workload <= workload)
        
        # Minimize the difference between max and min workload
        self.model.Minimize(max_workload - min_workload)
    
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
            duty_id = assignment.get('duty_id')
            if not duty_id:
                continue
                
            duty = self.get_duty_by_id(duty_id)
            if not duty:
                continue
                
            minutes = duty['working_minutes']
            
            for emp_name in assignment['assigned_employees']:
                emp = next((e for e in self.employees if e['name'] == emp_name), None)
                if not emp:
                    continue
                    
                emp_workloads[emp['id']] += minutes
        
        # Calculate average workload
        total_workload = sum(emp_workloads.values())
        avg_workload = total_workload / len(self.employees) if self.employees else 0
        
        # Check if any employee's workload deviates too much from the average
        return all(
            abs(workload - avg_workload) / avg_workload * 100 <= self.max_deviation_percent
            for workload in emp_workloads.values()
            if avg_workload > 0
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
        from datetime import datetime, timedelta
        
        start = datetime.strptime(start_time, "%H:%M")
        end = datetime.strptime(end_time, "%H:%M")
        
        # If end time is earlier than start time, it's an overnight duty
        if end < start:
            # Add 24 hours to the end time to get the correct duration
            end = end + timedelta(days=1)
        
        duration = end - start
        return duration.total_seconds() / 3600 