import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, date, timedelta

class ConfigLoader:
    """Class for loading configuration files for the Resource Planner."""
    
    def __init__(self, config_dir: str = "data/configurations"):
        """
        Initializes the ConfigLoader.
        
        Args:
            config_dir: Directory where the configuration files are stored
        """
        self.config_dir = config_dir
        
    def list_configurations(self) -> List[str]:
        """
        Lists all available configurations.
        
        Returns:
            List of names of available configurations
        """
        config_files = [f for f in os.listdir(self.config_dir) if f.endswith('.json')]
        return [os.path.splitext(f)[0] for f in config_files]
    
    def load_configuration(self, config_name: str) -> Dict[str, Any]:
        """
        Loads a configuration from a JSON file.
        
        Args:
            config_name: Name of the configuration (without .json extension)
            
        Returns:
            Dictionary with the configuration
            
        Raises:
            FileNotFoundError: If the configuration file was not found
            json.JSONDecodeError: If the JSON file is not properly formatted
        """
        config_path = os.path.join(self.config_dir, f"{config_name}.json")
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file {config_path} not found")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        # Validate the configuration
        self._validate_configuration(config)
        
        # Expand duties for each day in the date range
        config["duties"] = self._expand_duties(config)
        
        return config
    
    def _calculate_working_hours(self, start_time: str, end_time: str) -> float:
        """
        Calculates the working hours for a duty, handling overnight shifts.
        
        Args:
            start_time: Start time in format "HH:MM" or "H:MM"
            end_time: End time in format "HH:MM" or "H:MM"
            
        Returns:
            Number of working hours as a float
        """
        # Parse times
        start = datetime.strptime(start_time, "%H:%M")
        end = datetime.strptime(end_time, "%H:%M")
        
        # Calculate time difference
        if end < start:
            # Overnight shift
            end = end.replace(day=2)  # Add a day to end time
            start = start.replace(day=1)
        
        # Calculate hours
        delta = end - start
        return delta.total_seconds() / 3600  # Convert to hours
    
    def _expand_duties(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Expands duties for each day in the date range.
        
        Args:
            config: Dictionary with the configuration
            
        Returns:
            List of expanded duties with dates and IDs
        """
        start_date = datetime.strptime(config["start_date"], "%Y-%m-%d").date()
        end_date = datetime.strptime(config["end_date"], "%Y-%m-%d").date()
        
        expanded_duties = []
        duty_id = 0
        
        # Iterate through each day in the date range
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            
            # Create a duty for each template duty
            for duty_template in config["duties"]:
                duty = duty_template.copy()
                duty["date"] = date_str
                duty["id"] = duty_id
                duty["working_hours"] = self._calculate_working_hours(
                    duty["start_time"], 
                    duty["end_time"]
                )
                duty_id += 1
                expanded_duties.append(duty)
            
            current_date += timedelta(days=1)
        
        return expanded_duties
    
    def _validate_time_format(self, time_str: str) -> bool:
        """
        Validates if a time string is in a valid format (HH:MM or H:MM).
        
        Args:
            time_str: Time string to validate
            
        Returns:
            True if the format is valid, False otherwise
        """
        try:
            # Try parsing with leading zero format
            datetime.strptime(time_str, "%H:%M")
            return True
        except ValueError:
            try:
                # Try parsing without leading zero format
                datetime.strptime(time_str, "%I:%M")
                return True
            except ValueError:
                return False
    
    def _validate_configuration(self, config: Dict[str, Any]) -> None:
        """
        Validates a configuration.
        
        Args:
            config: Dictionary with the configuration
            
        Raises:
            ValueError: If the configuration is invalid
        """
        required_keys = ["name", "description", "start_date", "end_date", "employees", "duties"]
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Configuration must contain the key '{key}'")
        
        # Validate date formats
        try:
            start_date = datetime.strptime(config["start_date"], "%Y-%m-%d")
            end_date = datetime.strptime(config["end_date"], "%Y-%m-%d")
            if end_date < start_date:
                raise ValueError("end_date must be after start_date")
        except ValueError:
            raise ValueError("Invalid date format in start_date or end_date")
        
        # Validate employees
        for emp in config["employees"]:
            required_emp_keys = ["id", "name", "max_days_in_a_row", "off_days", "max_hours_per_day", 
                               "max_hours_in_period", "work_percentage"]
            for key in required_emp_keys:
                if key not in emp:
                    raise ValueError(f"Employee must contain the key '{key}'")
            
            # Validate off_days
            if not isinstance(emp["off_days"], list):
                raise ValueError(f"off_days must be a list, but is {type(emp['off_days'])}")
            
            # Validate date formats in off_days
            for off_day in emp["off_days"]:
                try:
                    off_date = datetime.strptime(off_day, "%Y-%m-%d").date()
                    if off_date < start_date.date() or off_date > end_date.date():
                        raise ValueError(f"off_day {off_day} is outside the configuration period")
                except ValueError:
                    raise ValueError(f"Invalid date format in off_days: {off_day}")
            
            # Validate numeric fields
            if not isinstance(emp["max_days_in_a_row"], int) or emp["max_days_in_a_row"] < 1:
                raise ValueError(f"max_days_in_a_row must be a positive integer")
            
            if not isinstance(emp["max_hours_per_day"], int) or emp["max_hours_per_day"] < 1:
                raise ValueError(f"max_hours_per_day must be a positive integer")
            
            if not isinstance(emp["max_hours_in_period"], int) or emp["max_hours_in_period"] < 1:
                raise ValueError(f"max_hours_in_period must be a positive integer")
            
            if not isinstance(emp["work_percentage"], int) or not 0 <= emp["work_percentage"] <= 100:
                raise ValueError(f"work_percentage must be an integer between 0 and 100")
        
        # Validate Duties
        for duty in config["duties"]:
            required_duty_keys = ["code", "required_employees", "start_time", "end_time"]
            for key in required_duty_keys:
                if key not in duty:
                    raise ValueError(f"Duty must contain the key '{key}'")
            
            # Validate time formats
            if not self._validate_time_format(duty["start_time"]) or not self._validate_time_format(duty["end_time"]):
                raise ValueError(f"Invalid time format in duty: {duty['start_time']} or {duty['end_time']}")
            
            # Validate required_employees
            if not isinstance(duty["required_employees"], int) or duty["required_employees"] < 1:
                raise ValueError(f"required_employees must be a positive integer")
    
    def get_employee_by_id(self, config: Dict[str, Any], emp_id: int) -> Optional[Dict[str, Any]]:
        """
        Finds an employee by their ID.
        
        Args:
            config: Dictionary with the configuration
            emp_id: ID of the employee
            
        Returns:
            Dictionary with the employee data or None if not found
        """
        for emp in config["employees"]:
            if emp["id"] == emp_id:
                return emp
        return None
    
    def get_duty_by_id(self, config: Dict[str, Any], duty_id: int) -> Optional[Dict[str, Any]]:
        """
        Finds a duty by its ID.
        
        Args:
            config: Dictionary with the configuration
            duty_id: ID of the duty
            
        Returns:
            Dictionary with the duty data or None if not found
        """
        for duty in config["duties"]:
            if duty["id"] == duty_id:
                return duty
        return None
    
    def get_duties_by_date(self, config: Dict[str, Any], date_str: str) -> List[Dict[str, Any]]:
        """
        Finds all duties on a specific date.
        
        Args:
            config: Dictionary with the configuration
            date_str: Date in format "YYYY-MM-DD"
            
        Returns:
            List of duties on this date
        """
        return [duty for duty in config["duties"] if duty["date"] == date_str]
    
    def get_employees_by_blocked_day(self, config: Dict[str, Any], date_str: str) -> List[Dict[str, Any]]:
        """
        Finds all employees who are blocked on a specific date.
        
        Args:
            config: Dictionary with the configuration
            date_str: Date in format "YYYY-MM-DD"
            
        Returns:
            List of blocked employees on this date
        """
        return [emp for emp in config["employees"] if date_str in emp["off_days"]] 