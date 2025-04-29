from typing import Dict, List, Any
from datetime import datetime, timedelta
from .base_constraint import BaseConstraint

class RestTimeConstraint(BaseConstraint):
    """
    Constraint ensuring employees have sufficient rest time between duties.
    
    This constraint ensures that if an employee is assigned to a duty that ends at time T,
    they cannot be assigned to another duty that starts before time T+8 (8 hours rest).
    """
    
    def __init__(self, model, assignments, employees, duties, min_rest_hours=8):
        """
        Initialize the rest time constraint.
        
        Args:
            model: The CP-SAT model
            assignments: Dictionary mapping (employee_id, duty_id) to solver variables
            employees: List of employee dictionaries
            duties: List of duty dictionaries
            min_rest_hours: Minimum rest hours required between duties (default: 8)
        """
        super().__init__(model, assignments, employees, duties)
        self.min_rest_hours = min_rest_hours
    
    def apply(self) -> None:
        """
        Apply the rest time constraint to the model.
        
        For each employee and each pair of duties, if the first duty ends at time T
        and the second duty starts before time T+min_rest_hours, the employee cannot
        be assigned to both duties.
        """
        # Create a mapping of duty IDs to their start and end times
        duty_times = {}
        for duty in self.duties:
            # Parse start and end times
            start_time = datetime.strptime(duty['start_time'], '%H:%M').time()
            end_time = datetime.strptime(duty['end_time'], '%H:%M').time()
            
            # Convert to datetime for easier comparison
            duty_date = datetime.strptime(duty['date'], '%Y-%m-%d').date()
            start_dt = datetime.combine(duty_date, start_time)
            end_dt = datetime.combine(duty_date, end_time)
            
            # Handle overnight duties
            if end_time < start_time:
                end_dt = end_dt + timedelta(days=1)
                
            duty_times[duty['id']] = (start_dt, end_dt)
        
        # For each employee and each pair of duties, check rest time
        for emp in self.employees:
            for duty1 in self.duties:
                for duty2 in self.duties:
                    if duty1['id'] == duty2['id']:
                        continue
                        
                    end1 = duty_times[duty1['id']][1]
                    start2 = duty_times[duty2['id']][0]
                    
                    # Calculate hours between end of duty1 and start of duty2
                    diff_hours = (start2 - end1).total_seconds() / 3600
                    
                    # If less than min_rest_hours between duties, add constraint
                    if 0 < diff_hours < self.min_rest_hours:
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
        # Create a mapping of duty IDs to their start and end times
        duty_times = {}
        for duty in self.duties:
            # Parse start and end times
            start_time = datetime.strptime(duty['start_time'], '%H:%M').time()
            end_time = datetime.strptime(duty['end_time'], '%H:%M').time()
            
            # Convert to datetime for easier comparison
            duty_date = datetime.strptime(duty['date'], '%Y-%m-%d').date()
            start_dt = datetime.combine(duty_date, start_time)
            end_dt = datetime.combine(duty_date, end_time)
            
            # Handle overnight duties
            if end_time < start_time:
                end_dt = end_dt + timedelta(days=1)
                
            duty_times[duty['id']] = (start_dt, end_dt)
        
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
                
                # Calculate hours between end of duty1 and start of duty2
                diff_hours = (start2 - end1).total_seconds() / 3600
                
                # If less than min_rest_hours between duties, constraint is violated
                if 0 < diff_hours < self.min_rest_hours:
                    return False
                    
        return True 