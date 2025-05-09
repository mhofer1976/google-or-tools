from typing import Dict, List, Any
from collections import defaultdict
from .base_constraint import BaseConstraint

class RequiredEmployeesConstraint(BaseConstraint):
    """
    Constraint ensuring each duty has the required number of employees assigned.
    """
    
    def apply(self) -> None:
        """
        Apply the required employees constraint to the model.
        
        For each duty, the sum of assignments must equal the required number of employees.
        """
        for duty in self.duties:
            required = duty['required_employees']
            # Sum of all employee assignments for this duty must equal required_employees
            emp_sum = sum(self.assignments[emp['id'], duty['id']] 
                         for emp in self.employees)
            self.model.Add(emp_sum == required)
    
    def _count_assignments_per_duty(self, assignments: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count how many employees are assigned to each duty."""
        duty_counts = defaultdict(int)
        for assignment in assignments:
            duty_counts[assignment['duty_id']] = len(assignment['employees'])
        return duty_counts
    
    def validate(self, assignments: List[Dict[str, Any]]) -> bool:
        """
        Validate that each duty has the required number of employees assigned.
        
        Args:
            assignments: List of assignment dictionaries from the solver
            
        Returns:
            True if all duties have the required number of employees, False otherwise
        """
        duty_counts = self._count_assignments_per_duty(assignments)
        
        # Only check duties that are in the assignments
        return all(
            duty_counts.get(duty['id'], 0) == duty['required_employees']
            for duty in self.duties
            if any(assignment['duty_id'] == duty['id'] for assignment in assignments)
        ) 