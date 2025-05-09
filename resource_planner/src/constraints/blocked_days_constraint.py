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
        [
            self.model.Add(self.assignments[emp['id'], duty['id']] == 0)
            for emp in self.employees
            for duty in self.duties
            if duty['date'] in set(emp['blocked_days'])
        ]
    
    def validate(self, assignments: List[Dict[str, Any]]) -> bool:
        """
        Validate that no employee is assigned to duties on their blocked days.
        
        Args:
            assignments: List of assignment dictionaries from the solver
            
        Returns:
            True if no employee is assigned on blocked days, False otherwise
        """
        return not any(
            assignment['date'] in set(emp['blocked_days'])
            for emp in self.employees
            for assignment in self.get_employee_assignments(assignments, emp['id'])
        ) 