from typing import Dict, List, Any
from .base_constraint import BaseConstraint

class BlockedDaysConstraint(BaseConstraint):
    """
    Constraint ensuring employees are not assigned to duties on their blocked days.
    """
    
    def apply(self) -> None:
        """
        Apply the blocked days constraint to the model.
        
        For each employee and each duty on a blocked day, the assignment must be 0.
        """
        for emp in self.employees:
            blocked = set(emp['blocked_days'])
            for duty in self.duties:
                if duty['date'] in blocked:
                    # Employee cannot be assigned to this duty (it's on a blocked day)
                    self.model.Add(self.assignments[emp['id'], duty['id']] == 0)
    
    def validate(self, solution: List[Dict[str, Any]]) -> bool:
        """
        Validate that no employee is assigned to duties on their blocked days.
        
        Args:
            solution: List of assignment dictionaries from the solver
            
        Returns:
            True if no employee is assigned on blocked days, False otherwise
        """
        for emp in self.employees:
            blocked_days = set(emp['blocked_days'])
            
            # Get all assignments for this employee
            emp_assignments = self.get_employee_assignments(solution, emp['id'])
            
            # Check if any assignment is on a blocked day
            for assignment in emp_assignments:
                if assignment['date'] in blocked_days:
                    return False
                    
        return True 