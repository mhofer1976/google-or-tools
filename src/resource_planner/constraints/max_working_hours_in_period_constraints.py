from typing import Dict, List, Any
from .base_constraint import BaseConstraint

class MaxWorkingHoursInPeriodConstraints(BaseConstraint):
    """
    Constraint ensuring employees don't work more than their maximum allowed working hours.
    """
    
    def apply(self) -> None:
        """
        Apply the max working hours constraint to the model.
        
        For each employee ensure that the sum of their working hours is less than max_working_hours_in_period.
        """
        for emp in self.employees:
            # Calculate total working minutes by summing up the product of each assignment variable
            # with its corresponding duty's working minutes
            total_minutes = sum(
                self.assignments[emp['id'], duty['id']] * duty['working_minutes']
                for duty in self.duties
            )
            
            # Convert max hours to minutes and ensure total minutes doesn't exceed maximum
            max_minutes = int(emp['max_hours_in_period']) * 60
            self.model.Add(total_minutes <= max_minutes)
    
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
            
            # Check if total hours exceed maximum
            if total_minutes / 60 > emp['max_hours_in_period']:
                return False
                
        return True 