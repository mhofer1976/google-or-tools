from typing import Dict, List, Any, Optional
from datetime import datetime, date, timedelta
from .resource_planner import ResourcePlanner
from .config_loader import ConfigLoader

class ResourcePlanningService:
    """Class that uses the ResourcePlanner with configuration data."""
    
    def __init__(self, config_name: str, config_dir: str = "data/configurations"):
        """
        Initializes the ResourcePlanningService.
        
        Args:
            config_name: Name of the configuration (without .json extension)
            config_dir: Directory where the configuration files are stored
        """
        self.config_loader = ConfigLoader(config_dir)
        self.config = self.config_loader.load_configuration(config_name)
        self.planner = ResourcePlanner()
        self._setup_planner()
        
    def _setup_planner(self) -> None:
        """Sets up the ResourcePlanner with the configuration data."""
        # Add employees
        for emp in self.config["employees"]:
            self.planner.add_employee(
                emp["id"],
                emp["name"],
                emp["max_days_in_a_row"],
                emp["off_days"],
                emp["max_hours_per_day"],
                emp["max_hours_in_period"],
                emp["work_percentage"]
            )
        
        # Add duties
        for duty in self.config["duties"]:
            self.planner.add_duty(
                duty["code"],
                duty["required_employees"],
                duty["start_time"],
                duty["end_time"]
            )
        
        # Set up the model
        self.planner.setup_model()
        
    def solve(self) -> List[Dict[str, Any]]:
        """
        Solves the planning problem.
        
        Returns:
            List of assignments
        """
        return self.planner.solve()
    
    def get_configuration_info(self) -> Dict[str, Any]:
        """
        Returns information about the configuration.
        
        Returns:
            Dictionary with information about the configuration
        """
        return {
            "name": self.config["name"],
            "description": self.config["description"],
            "start_date": self.config["start_date"],
            "end_date": self.config["end_date"],
            "num_employees": len(self.config["employees"]),
            "num_duties": len(self.config["duties"])
        }
    
    def get_employee_assignments(self, emp_id: int) -> List[Dict[str, Any]]:
        """
        Returns all assignments for a specific employee.
        
        Args:
            emp_id: ID of the employee
            
        Returns:
            List of assignments for this employee
        """
        emp = self.config_loader.get_employee_by_id(self.config, emp_id)
        if not emp:
            return []
        
        assignments = self.solve()
        return [
            assignment for assignment in assignments
            if emp["name"] in assignment["assigned_employees"]
        ]
    
    def get_duty_assignments(self, duty_code: str) -> List[Dict[str, Any]]:
        """
        Returns the assignments for a specific duty.
        
        Args:
            duty_code: Code of the duty
            
        Returns:
            List of assignments for this duty
        """
        assignments = self.solve()
        return [
            assignment for assignment in assignments
            if assignment["duty_code"] == duty_code
        ]
    
    def get_assignments_by_date(self, date_str: str) -> List[Dict[str, Any]]:
        """
        Returns all assignments on a specific date.
        
        Args:
            date_str: Date in format "YYYY-MM-DD"
            
        Returns:
            List of assignments on this date
        """
        assignments = self.solve()
        return [
            assignment for assignment in assignments
            if assignment["date"] == date_str
        ]
    
    def get_workload_distribution(self) -> Dict[str, float]:
        """
        Calculates the workload distribution across all employees.
        
        Returns:
            Dictionary with employee names and their working hours
        """
        assignments = self.solve()
        workload = {}
        
        for assignment in assignments:
            # Get the duty to access its working_hours
            duty = self.config_loader.get_duty_by_id(self.config, assignment["duty_id"])
            if duty:
                hours = duty["working_hours"]
            else:
                # Fallback to calculating hours if duty not found
                hours = self._calculate_duty_hours(
                    assignment["start_time"],
                    assignment["end_time"]
                )
            
            for emp_name in assignment["assigned_employees"]:
                if emp_name not in workload:
                    workload[emp_name] = 0
                workload[emp_name] += hours
        
        return workload
    
    def _calculate_duty_hours(self, start_time: str, end_time: str) -> float:
        """
        Calculates the number of hours for a duty, handling overnight duties correctly.
        This is a fallback method if the working_hours field is not available.
        
        Args:
            start_time: Start time in format "HH:MM"
            end_time: End time in format "HH:MM"
            
        Returns:
            Number of hours the duty lasts
        """
        start = datetime.strptime(start_time, "%H:%M")
        end = datetime.strptime(end_time, "%H:%M")
        
        # If end time is earlier than start time, it's an overnight duty
        if end < start:
            # Add 24 hours to the end time to get the correct duration
            end = end + timedelta(days=1)
        
        duration = end - start
        return duration.total_seconds() / 3600 