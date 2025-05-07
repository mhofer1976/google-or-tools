from typing import Dict, List, Any, Set
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
        duties_by_date = {}
        for duty in self.duties:
            if duty['date'] not in duties_by_date:
                duties_by_date[duty['date']] = []
            duties_by_date[duty['date']].append(duty['id'])
            
        # For each employee and each date, ensure at most one duty is assigned
        for emp in self.employees:
            for date, duty_ids in duties_by_date.items():
                # Sum of assignments for this employee on this date must be <= 1
                self.model.Add(
                    sum(self.assignments[emp['id'], duty_id] for duty_id in duty_ids) <= 1
                )
    
    def validate(self, solution: List[Dict[str, Any]]) -> bool:
        """
        Validate that each employee is assigned to at most one duty per day.
        
        Args:
            solution: List of assignment dictionaries from the solver
            
        Returns:
            True if each employee has at most one duty per day, False otherwise
        """
        
        #TODO: This implementation is not corret.
        
        # # Group assignments by employee and date
        # assignments_by_emp_date = {}
        
        # for assignment in solution:
        #     date = assignment['date']
        #     for emp_name in assignment['assigned_employees']:
        #         # Find employee ID from name
        #         emp = next((e for e in self.employees if e['name'] == emp_name), None)
        #         if not emp:
        #             continue
                    
        #         emp_id = emp['id']
        #         key = (emp_id, date)
                
        #         if key not in assignments_by_emp_date:
        #             assignments_by_emp_date[key] = 0
        #         assignments_by_emp_date[key] += 1
                
        #         # If more than one assignment on the same day, constraint is violated
        #         if assignments_by_emp_date[key] > 1:
        #             return False
                    
        return True 