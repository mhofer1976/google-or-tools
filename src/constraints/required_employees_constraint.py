from typing import Dict, List, Any
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
    
    def validate(self, solution: List[Dict[str, Any]]) -> bool:
        """
        Validate that each duty has the required number of employees assigned.
        
        Args:
            solution: List of assignment dictionaries from the solver
            
        Returns:
            True if all duties have the required number of employees, False otherwise
        """
        for duty in self.duties:
            # Find this duty in the solution
            duty_assignments = next(
                (assignment for assignment in solution 
                 if assignment.get('duty_id') == duty['id']),
                None
            )
            
            if not duty_assignments:
                # If duty not found in solution, it's a validation failure
                return False
                
            # Check if the number of assigned employees matches the required number
            if len(duty_assignments['assigned_employees']) != duty['required_employees']:
                return False
                
        return True 