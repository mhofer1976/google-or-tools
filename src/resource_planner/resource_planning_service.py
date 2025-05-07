from typing import Dict, List, Any, Optional, Union
from datetime import datetime, date, timedelta
import json
import os
from .resource_planner import ResourcePlanner
from .config_loader import ConfigLoader
from .constraints import (
    RequiredEmployeesConstraint,
    BlockedDaysConstraint,
    OneDutyPerDayConstraint,
    RestTimeConstraint,
    MaxDaysInARowConstraint,
    WorkloadBalanceConstraint,
)

class ResourcePlanningService:
    """
    Service that uses the ResourcePlanner with configuration data.
    
    This service loads configuration data and uses it to set up and solve
    resource planning problems using the constraint-based ResourcePlanner.
    
    The service can be initialized in two ways:
    1. With a configuration name (which gets loaded from the config directory)
    2. With a direct configuration JSON (for API/external calls)
    """
    
    def __init__(self, config_source: Union[str, Dict[str, Any]], config_dir: str = "data/resource_planner/configurations"):
        """
        Initialize the ResourcePlanningService.
        
        Args:
            config_source: Either a configuration name (string) or a configuration dictionary
            config_dir: Directory containing configuration files (only used if config_source is a string)
        """
        self.config_loader = ConfigLoader(config_dir)
        
        # Handle different types of config_source
        if isinstance(config_source, str):
            # Load configuration by name
            self.config = self.config_loader.load_configuration_by_name(config_source)
            self.config_name = config_source
        else:
            # Use provided configuration directly
            self.config = config_source
            self.config_name = self.config.get("name", "direct_config")
            
        self.config_loader.validate_configuration(self.config)
                        
        self.planner = ResourcePlanner()
        self._setup_planner()
        
    def _setup_planner(self) -> None:
        """Set up the planner with employees, duties, and constraints from the configuration."""
        # Add employees
        for emp in self.config["employees"]:
            self.planner.add_employee(
                emp["id"],
                emp["name"],
                emp["max_days_in_a_row"],
                emp["off_days"],
                emp["max_hours_per_day"],
                emp["max_hours_in_period"]
            )
        
        # Add duties
        for duty in self.config["duties"]:
            self.planner.add_duty(
                duty["id"],
                duty["code"],
                duty["date"],
                duty["required_employees"],
                duty["start_time"],
                duty["end_time"],
                duty["working_minutes"]
            )
        
        # Add constraints
        self.planner.add_constraint(RequiredEmployeesConstraint)
        self.planner.add_constraint(BlockedDaysConstraint)
        # self.planner.add_constraint(OneDutyPerDayConstraint)
        # self.planner.add_constraint(RestTimeConstraint)
        # self.planner.add_constraint(MaxDaysInARowConstraint)
        # self.planner.add_constraint(WorkloadBalanceConstraint)
        
        # Setup the model
        self.planner.setup_model()
        
    def solve(self) -> Dict[str, Any]:
        """
        Solve the planning problem and save input/output to debug files.
        
        Returns:
            Dictionary containing:
            - date: The date when solving started
            - start_time: When solving started
            - end_time: When solving finished
            - duration_seconds: How long solving took
            - status: The solver status (OPTIMAL, FEASIBLE, or INFEASIBLE)
            - assignments: List of solved assignments with duty and employee information
        """
        # Generate timestamp for filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create debug directory if it doesn't exist
        debug_dir = "data/resource_planner/debug"
        os.makedirs(debug_dir, exist_ok=True)
        
        # Save input configuration
        input_filename = f"{debug_dir}/input_{timestamp}.json"
        with open(input_filename, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        # Record start time
        start_datetime = datetime.now()
        
        # Solve the problem
        status = self.planner.solve()
        assignments = self.planner.assignments
        
        # Record end time
        end_datetime = datetime.now()
        
        # Calculate duration
        duration = (end_datetime - start_datetime).total_seconds()
        
        # Construct result object
        result = {
            "date": start_datetime.strftime("%Y-%m-%d"),
            "start_time": start_datetime.strftime("%H:%M:%S"),
            "end_time": end_datetime.strftime("%H:%M:%S"),
            "duration_seconds": duration,
            "status": status.value,  # Get the string value from the enum
            "assignments": assignments
        }
        
        # Save output assignments
        output_filename = f"{debug_dir}/output_{timestamp}.json"
        with open(output_filename, 'w') as f:
            json.dump(result, f, indent=2)
        
        return result
    
    
        # """
        # Calculate the workload distribution across all employees.
        
        # Returns:
        #     Dictionary mapping employee names to their total working hours
        # """
        # assignments = self.solve()
        # workload = {}
        
        # for assignment in assignments:
        #     # Get the duty to access its working_hours
        #     duty = self.config_loader.get_duty_by_id(self.config, assignment["duty_id"])
        #     if duty:
        #         hours = duty["working_hours"]
        #     else:
        #         # Fallback to calculating hours if duty not found
        #         hours = self._calculate_duty_hours(
        #             assignment["start_time"],
        #             assignment["end_time"]
        #         )
            
        #     for emp_name in assignment["assigned_employees"]:
        #         if emp_name not in workload:
        #             workload[emp_name] = 0
        #         workload[emp_name] += hours
        
        # return workload
    
    # def _calculate_duty_hours(self, start_time: str, end_time: str) -> float:
    #     """
    #     Calculate the number of hours for a duty, handling overnight duties correctly.
        
    #     Args:
    #         start_time: Start time in format "HH:MM"
    #         end_time: End time in format "HH:MM"
            
    #     Returns:
    #         Number of hours the duty lasts
    #     """
    #     start = datetime.strptime(start_time, "%H:%M")
    #     end = datetime.strptime(end_time, "%H:%M")
        
    #     # If end time is earlier than start time, it's an overnight duty
    #     if end < start:
    #         # Add 24 hours to the end time to get the correct duration
    #         end = end + timedelta(days=1)
        
    #     duration = end - start
    #     return duration.total_seconds() / 3600
    
    @classmethod
    def list_available_configurations(cls, config_dir: str = "data/resource_planner/configurations") -> List[str]:
        """
        List all available configuration names.
        
        Args:
            config_dir: Directory containing configuration files
            
        Returns:
            List of available configuration names
        """
        return ConfigLoader(config_dir).list_configurations()
    
    @classmethod
    def validate_configuration(cls, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a configuration dictionary.
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            Dictionary with validation results:
                - valid: Boolean indicating if the configuration is valid
                - errors: List of error messages (empty if valid)
        """
        config_loader = ConfigLoader()
        try:
            # Use the config_loader's validation method
            config_loader._validate_configuration(config)
            return {"valid": True, "errors": []}
        except ValueError as e:
            return {"valid": False, "errors": [str(e)]}
        except Exception as e:
            return {"valid": False, "errors": [f"Unexpected error: {str(e)}"]}
    
    # def to_json(self) -> str:
    #     """
    #     Convert the current configuration to a JSON string.
        
    #     Returns:
    #         JSON string representation of the configuration
    #     """
    #     return json.dumps(self.config, indent=2) 