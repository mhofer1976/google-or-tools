from typing import Dict, List, Any
from .base_constraint import BaseConstraint

class MaxWorkingMinsInPeriodConstraints(BaseConstraint):
    """
    Constraint ensuring employees don't work more than their maximum allowed working minutes.
    """
    
    def apply(self) -> None:
        """
        Apply the max working minutes constraint to the model.
        
        For each employee ensure that the sum of their working minutes is less than max_working_mins_in_period.
        """
        for emp in self.employees:
            # Get all assignments for this employee
            emp_assignments = self.get_employee_assignments(self.assignments, emp['id'])
            
            # Sum up working minutes for all assigned duties
            assigned_mins_sum = sum(
                self.get_duty_by_id(assignment['duty_id'])['working_minutes']
                for assignment in emp_assignments
            )
            
            # Ensure total minutes doesn't exceed maximum
            self.model.Add(assigned_mins_sum <= emp['max_working_mins_in_period'])
    
    def validate(self, assignments: List[Dict[str, Any]]) -> bool:
        """
        Validate that no employee works more than their maximum allowed working minutes.
        
        Args:
            assignments: List of assignment dictionaries from the solver
            
        Returns:
            True if no employee exceeds their maximum working minutes, False otherwise
        """
        for emp in self.employees:
            # Get all assignments for this employee
            emp_assignments = self.get_employee_assignments(assignments, emp['id'])
            
            # Sum up working minutes for all assigned duties
            total_minutes = sum(
                self.get_duty_by_id(assignment['duty_id'])['working_minutes']
                for assignment in emp_assignments
            )
            
            # Check if total minutes exceed maximum
            if total_minutes > emp['max_working_mins_in_period']:
                return False
                
        return True 