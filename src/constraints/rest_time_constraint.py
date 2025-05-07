from typing import Dict, List, Any
from datetime import datetime, timedelta
from .base_constraint import BaseConstraint

class RestTimeConstraint(BaseConstraint):
    """
    Constraint ensuring employees have sufficient rest time between duties.
    
    This constraint ensures that employees have at least min_rest_hours hours
    of rest between consecutive duties.
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
    
    def apply(self) -> None:
        """
        Apply the rest time constraint to the model.
        
        For each employee and each pair of duties, if the time between the end
        of one duty and the start of another is less than min_rest_minutes,
        the employee cannot be assigned to both duties.
        """
        # Pre-calculate duty times to avoid repeated parsing
        duty_times = {}
        for duty in self.duties:
            start = datetime.strptime(duty['start_time'], "%H:%M")
            end = datetime.strptime(duty['end_time'], "%H:%M")
            
            # Handle overnight duties
            if end < start:
                end = end + timedelta(days=1)
                
            duty_times[duty['id']] = (start, end)
        
        # For each employee and each pair of duties, check rest time
        for emp in self.employees:
            for duty1 in self.duties:
                for duty2 in self.duties:
                    if duty1['id'] == duty2['id']:
                        continue
                        
                    end1 = duty_times[duty1['id']][1]
                    start2 = duty_times[duty2['id']][0]
                    
                    # Calculate minutes between end of duty1 and start of duty2
                    diff_minutes = int((start2 - end1).total_seconds() / 60)
                    
                    # If less than min_rest_minutes between duties, add constraint
                    if 0 < diff_minutes < self.min_rest_minutes:
                        self.model.Add(
                            self.assignments[emp['id'], duty1['id']] + 
                            self.assignments[emp['id'], duty2['id']] <= 1
                        )
    
    def validate(self, solution: List[Dict[str, Any]]) -> bool:
        """
        Validate that all employees have sufficient rest time between duties.
        
        Args:
            solution: List of assignment dictionaries from the solver
            
        Returns:
            True if all employees have sufficient rest time, False otherwise
        """
        # Pre-calculate duty times to avoid repeated parsing
        duty_times = {}
        for duty in self.duties:
            start = datetime.strptime(duty['start_time'], "%H:%M")
            end = datetime.strptime(duty['end_time'], "%H:%M")
            
            # Handle overnight duties
            if end < start:
                end = end + timedelta(days=1)
                
            duty_times[duty['id']] = (start, end)
        
        # For each employee, check rest time between all assigned duties
        for emp in self.employees:
            # Get all assignments for this employee
            emp_assignments = self.get_employee_assignments(solution, emp['id'])
            
            # Sort assignments by start time
            sorted_assignments = sorted(
                emp_assignments,
                key=lambda a: duty_times[a['duty_id']][0]
            )
            
            # Check rest time between consecutive assignments
            for i in range(len(sorted_assignments) - 1):
                duty1_id = sorted_assignments[i]['duty_id']
                duty2_id = sorted_assignments[i+1]['duty_id']
                
                end1 = duty_times[duty1_id][1]
                start2 = duty_times[duty2_id][0]
                
                # Calculate minutes between end of duty1 and start of duty2
                diff_minutes = int((start2 - end1).total_seconds() / 60)
                
                # If less than min_rest_minutes between duties, constraint is violated
                if 0 < diff_minutes < self.min_rest_minutes:
                    return False
                    
        return True 