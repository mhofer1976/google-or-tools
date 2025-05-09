from typing import Dict, List, Any
from datetime import datetime, timedelta
from .base_constraint import BaseConstraint

class RestTimeConstraint(BaseConstraint):
    """
    Constraint ensuring employees have sufficient rest time between duties.
    
    This constraint ensures that employees have at least min_rest_hours hours
    of rest between consecutive duties, taking into account both dates and times.
    """
    
    def __init__(self, model, assignments, employees, duties, min_rest_hours=8):
        """
        Initialize the rest time constraint.
        
        Args:
            model: The CP-SAT model
            assignments: Dictionary mapping (employee_id, duty_id) to solver variables
            employees: List of employee dictionaries
            duties: List of duty dictionaries
            min_rest_hours: Minimum required rest time in hours (default: 8)
        """
        super().__init__(model, assignments, employees, duties)
        self.min_rest_minutes = min_rest_hours * 60  # Convert to minutes
        self._duty_times = self._calculate_duty_times()
    
    def _parse_datetime(self, date_str: str, time_str: str) -> datetime:
        """Parse date and time strings to datetime object."""
        return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    
    def _calculate_duty_times(self) -> Dict[str, Dict[str, datetime]]:
        """Calculate start and end times for all duties."""
        duty_times = {}
        for duty in self.duties:
            # Parse start time with date
            start = self._parse_datetime(duty['date'], duty['start_time'])
            
            # Parse end time with date
            end = self._parse_datetime(duty['date'], duty['end_time'])
            
            # Handle overnight duties (end time is on next day)
            if end < start:
                end = end + timedelta(days=1)
                
            duty_times[int(duty['id'])] = {
                'start': start,
                'end': end
            }
        return duty_times
    
    def _get_rest_minutes(self, end_time: datetime, start_time: datetime) -> int:
        """
        Calculate rest time in minutes between two duties.
        
        This takes into account both dates and times. For example:
        - Duty1 ends on 2025-01-01 23:00
        - Duty2 starts on 2025-01-02 02:00
        - Rest time would be 3 hours (180 minutes)
        """
        return int((start_time - end_time).total_seconds() / 60)
    
    def apply(self) -> None:
        """
        Apply the rest time constraint to the model.
        
        For each employee and each pair of duties, if the time between the end
        of one duty and the start of another is less than min_rest_minutes,
        the employee cannot be assigned to both duties.
        """
        for emp in self.employees:
            for duty1 in self.duties:
                for duty2 in self.duties:
                    if duty1['id'] == duty2['id']:
                        continue
                        
                    end1 = self._duty_times[duty1['id']]['end']
                    start2 = self._duty_times[duty2['id']]['start']
                    
                    # Calculate minutes between end of duty1 and start of duty2
                    diff_minutes = self._get_rest_minutes(end1, start2)
                    
                    # If less than min_rest_minutes between duties, add constraint
                    if 0 < diff_minutes < self.min_rest_minutes:
                        key1 = f"{emp['id']}_{duty1['id']}"
                        key2 = f"{emp['id']}_{duty2['id']}"
                        self.model.Add(
                            self.assignments[key1] + 
                            self.assignments[key2] <= 1
                        )
    
    def validate(self, assignments: List[Dict[str, Any]]) -> bool:
        """
        Validate that employees have sufficient rest time between duties.
        
        Args:
            assignments: List of assignment dictionaries from the solver
            
        Returns:
            True if all employees have sufficient rest time, False otherwise
        """
        for emp in self.employees:
            emp_assignments = self.get_employee_assignments(assignments, emp['id'])
            
            # Sort assignments by start time
            sorted_assignments = sorted(
                emp_assignments,
                key=lambda x: self._parse_datetime(x['date'], x['start_time'])
            )
            
            # Check rest time between consecutive assignments
            for i in range(len(sorted_assignments) - 1):
                current = sorted_assignments[i]
                next_duty = sorted_assignments[i + 1]
                
                end_time = self._parse_datetime(current['date'], current['end_time'])
                start_time = self._parse_datetime(next_duty['date'], next_duty['start_time'])
                
                rest_minutes = self._get_rest_minutes(end_time, start_time)
                if rest_minutes < self.min_rest_minutes:
                    return False
                    
        return True 