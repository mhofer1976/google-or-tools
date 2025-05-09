from typing import Dict, List, Any
from datetime import datetime
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
    
    def _get_assignments_by_date(self, assignments: List[Dict[str, Any]]) -> Dict[datetime, List[Dict[str, Any]]]:
        """Group assignments by date."""
        assignments_by_date = {}
        for assignment in assignments:
            date = assignment['date']
            assignments_by_date.setdefault(date, []).append(assignment)
        return assignments_by_date

    def _count_days_worked_in_window(self, window: List[datetime], assignments_by_date: Dict[datetime, List[Dict[str, Any]]]) -> int:
        """Count how many days in the window have assignments."""
        return sum(1 for date in window if date in assignments_by_date and assignments_by_date[date])

    def validate(self, solution: List[Dict[str, Any]]) -> bool:
        """
        Validate that no employee works more than the maximum allowed days in a row.
        
        Args:
            solution: List of assignment dictionaries from the solver
            
        Returns:
            True if no employee works more than max_days_in_a_row in a row, False otherwise
        """
        dates_sorted = sorted(set(duty['date'] for duty in self.duties))
        
        for emp in self.employees:
            max_days = emp['max_days_in_a_row']
            emp_assignments = self.get_employee_assignments(solution, emp['id'])
            assignments_by_date = self._get_assignments_by_date(emp_assignments)
            
            # Check each window of max_days + 1 consecutive days
            windows = (dates_sorted[i:i + max_days + 1] for i in range(len(dates_sorted) - max_days + 1))
            
            if any(self._count_days_worked_in_window(window, assignments_by_date) > max_days for window in windows):
                return False
                
        return True 