from typing import Dict, List, Any, Set
from datetime import datetime, timedelta
from .base_constraint import BaseConstraint

class MaxDaysInARowConstraint(BaseConstraint):
    """
    Constraint ensuring employees don't work more than the maximum allowed days in a row.
    """
    
    def apply(self) -> None:
        """
        Apply the max days in a row constraint to the model.
        
        For each employee and each window of max_days_in_a_row + 1 consecutive days,
        ensure the employee doesn't work more than max_days_in_a_row days in that window.
        """
        # Get all unique dates and sort them
        dates_sorted = sorted(set(duty['date'] for duty in self.duties))
        
        for emp in self.employees:
            max_days = emp['max_days_in_a_row']
            
            # For each window of max_days + 1 consecutive days
            for i in range(len(dates_sorted) - max_days + 1):
                window = dates_sorted[i:i + max_days + 1]  # +1 to check one more day
                
                # For each day in the window, check if the employee works on that day
                day_assignments = []
                for date in window:
                    # Find all duties on this date
                    day_duties = [d['id'] for d in self.duties if d['date'] == date]
                    
                    # Sum of assignments for this employee on this date
                    day_sum = sum(self.assignments[emp['id'], duty_id] for duty_id in day_duties)
                    day_assignments.append(day_sum)
                
                # Ensure no more than max_days_in_a_row consecutive days are worked
                self.model.Add(sum(day_assignments) <= max_days)
    
    def validate(self, solution: List[Dict[str, Any]]) -> bool:
        """
        Validate that no employee works more than the maximum allowed days in a row.
        
        Args:
            solution: List of assignment dictionaries from the solver
            
        Returns:
            True if no employee works more than max_days_in_a_row in a row, False otherwise
        """
        # Get all unique dates and sort them
        dates_sorted = sorted(set(duty['date'] for duty in self.duties))
        
        for emp in self.employees:
            max_days = emp['max_days_in_a_row']
            
            # Get all assignments for this employee
            emp_assignments = self.get_employee_assignments(solution, emp['id'])
            
            # Group assignments by date
            assignments_by_date = {}
            for assignment in emp_assignments:
                date = assignment['date']
                if date not in assignments_by_date:
                    assignments_by_date[date] = []
                assignments_by_date[date].append(assignment)
            
            # Check each window of max_days + 1 consecutive days
            for i in range(len(dates_sorted) - max_days + 1):
                window = dates_sorted[i:i + max_days + 1]  # +1 to check one more day
                
                # Count days worked in this window
                days_worked = 0
                for date in window:
                    if date in assignments_by_date and assignments_by_date[date]:
                        days_worked += 1
                
                # If more than max_days_in_a_row days worked in this window, constraint is violated
                if days_worked > max_days:
                    return False
                    
        return True 