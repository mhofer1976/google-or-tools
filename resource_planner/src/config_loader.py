import json
import os
from typing import Dict, List, Any
from datetime import datetime, timedelta

DEFAULT_CONFIG_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__), 
    '..', 
    'data', 
    'configurations'
))

class ConfigLoader:
    """Class for loading configuration files for the Resource Planner."""
    
    def __init__(self, config_dir: str = DEFAULT_CONFIG_DIR):
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
    
    def load_configuration_by_name(self, config_name: str) -> Dict[str, Any]:
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
                    
        # Expand duties for each day in the date range
        config["duties"] = self._expand_duties(config)
                
        return config

    def validate_configuration(self, config: Dict[str, Any]) -> None:
        """
        Validates a configuration.
        
        Args:
            config: Dictionary with the configuration
            
        Raises:
            ValueError: If the configuration is invalid
        """
        # Validate top-level required keys
        required_keys = ["name", "description", "start_date", "end_date", "employees", "duties"]
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Configuration must contain the key '{key}'")
        
        # Validate date formats and range
        try:
            start_date = datetime.strptime(config["start_date"], "%Y-%m-%d")
            end_date = datetime.strptime(config["end_date"], "%Y-%m-%d")
            if end_date < start_date:
                raise ValueError("end_date must be after start_date")
        except ValueError:
            raise ValueError("Invalid date format in start_date or end_date")
        
        # Validate employees
        employee_ids = set()
        for emp in config["employees"]:
            # Check required employee fields
            required_emp_keys = ["id", "name", "max_days_in_a_row", "off_days", 
                               "max_hours_per_day", "max_hours_in_period", "work_percentage"]
            for key in required_emp_keys:
                if key not in emp:
                    raise ValueError(f"Employee must contain the key '{key}'")
            
            # Validate employee ID uniqueness
            if emp["id"] in employee_ids:
                raise ValueError(f"Duplicate employee ID: {emp['id']}")
            employee_ids.add(emp["id"])
            
            # Validate off_days format and content
            if not isinstance(emp["off_days"], list):
                raise ValueError(f"off_days must be a list, but is {type(emp['off_days'])}")
            
            # Filter and validate off days
            valid_off_days = []
            for off_day in emp["off_days"]:
                try:
                    off_date = datetime.strptime(off_day, "%Y-%m-%d").date()
                    if start_date.date() <= off_date <= end_date.date():
                        valid_off_days.append(off_day)
                except ValueError:
                    raise ValueError(f"Invalid date format in off_days: {off_day}")
            emp["off_days"] = valid_off_days
            
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
        duty_ids = set()
        for duty in config["duties"]:
            # Check required duty fields
            required_duty_keys = ["id", "code", "date", "start_time", "end_time", "working_minutes"]
            for key in required_duty_keys:
                if key not in duty:
                    raise ValueError(f"Duty must contain the key '{key}'")
            
            # Validate duty ID uniqueness
            if duty["id"] in duty_ids:
                raise ValueError(f"Duplicate duty ID: {duty['id']}")
            duty_ids.add(duty["id"])
            
            # Validate date format and range
            try:
                duty_date = datetime.strptime(duty["date"], "%Y-%m-%d").date()
                if not (start_date.date() <= duty_date <= end_date.date()):
                    raise ValueError(f"Duty date {duty['date']} is outside the configured period")
            except ValueError:
                raise ValueError(f"Invalid date format in duty: {duty['date']}")
            
            # Validate time formats
            if not self._validate_time_format(duty["start_time"]) or not self._validate_time_format(duty["end_time"]):
                raise ValueError(f"Invalid time format in duty: {duty['start_time']} or {duty['end_time']}")
            
            # Validate working_minutes
            if not isinstance(duty["working_minutes"], int) or duty["working_minutes"] <= 0:
                raise ValueError(f"working_minutes must be a positive integer, got {duty['working_minutes']}")

    def _calculate_working_minutes(self, start_time: str, end_time: str) -> int:
        """
        Calculates the working minutes for a duty, handling overnight shifts.
        
        Args:
            start_time: Start time in format "HH:MM" or "H:MM"
            end_time: End time in format "HH:MM" or "H:MM"
            
        Returns:
            Number of working minutes as an integer
        """
        # Parse times
        start = datetime.strptime(start_time, "%H:%M")
        end = datetime.strptime(end_time, "%H:%M")
        
        # Calculate time difference
        if end < start:
            # Overnight shift
            end = end.replace(day=2)  # Add a day to end time
            start = start.replace(day=1)
        
        # Calculate minutes
        delta = end - start
        return int(delta.total_seconds() / 60)  # Convert to minutes
    
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
                duty["working_minutes"] = self._calculate_working_minutes(
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
