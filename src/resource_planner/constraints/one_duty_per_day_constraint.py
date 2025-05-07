from typing import Dict, List, Any, Set
from collections import defaultdict
from .base_constraint import BaseConstraint

class OneDutyPerDayConstraint(BaseConstraint):
    """
    Constraint ensuring each employee is assigned to at most one duty per day.
    """
    
    def apply(self) -> None:
        """
        Apply the one duty per day constraint to the model.
        
        For each employee and each day, the sum of assignments must be <= 1.
        """
        # Group duties by date
        duties_by_date = defaultdict(list)
        for duty in self.duties:
            duties_by_date[duty['date']].append(duty['id'])
            
        # For each employee and each date, ensure at most one duty is assigned
        for emp in self.employees:
            for duty_ids in duties_by_date.values():
                # Sum of assignments for this employee on this date must be <= 1
                self.model.Add(
                    sum(self.assignments[emp['id'], duty_id] for duty_id in duty_ids) <= 1
                )
    
    def _count_assignments_per_employee_and_date(self, assignments: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count how many duties each employee is assigned per day."""
        assignments_by_emp_date = defaultdict(int)
        
        for assignment in assignments:
            date = assignment['date']
            # Count each employee assigned to this duty
            for employee in assignment['employees']:
                emp_id = employee['employee_id']
                key = f"{emp_id}_{date}"
                assignments_by_emp_date[key] += 1
            
        return assignments_by_emp_date
    
    def validate(self, assignments: List[Dict[str, Any]]) -> bool:
        """
        Validate that each employee is assigned to at most one duty per day.
        
        Args:
            assignments: List of assignment dictionaries from the solver
            
        Returns:
            True if each employee has at most one duty per day, False otherwise
        """
        assignments_by_emp_date = self._count_assignments_per_employee_and_date(assignments)
        
        return all(count <= 1 for count in assignments_by_emp_date.values()) 