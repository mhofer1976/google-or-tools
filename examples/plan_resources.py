#!/usr/bin/env python
"""
Example script demonstrating how to use the ResourcePlanningService.
"""

import sys
import os
import json
from datetime import datetime

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.resource_planning_service import ResourcePlanningService

def run_with_config_name():
    """Run the resource planning example using a configuration name."""
    print("\n=== Using configuration by name ===")
    
    # List available configurations
    configs = ResourcePlanningService.list_available_configurations()
    print(f"Available configurations: {', '.join(configs)}")
    
    # Create a service instance with the OGE configuration
    service = ResourcePlanningService("oge")
    
    # Get configuration information
    config_info = service.get_configuration_info()
    print(f"Configuration: {config_info['name']}")
    print(f"Description: {config_info['description']}")
    print(f"Period: {config_info['start_date']} to {config_info['end_date']}")
    print(f"Employees: {config_info['num_employees']}")
    print(f"Duties: {config_info['num_duties']}")
    print()
    
    # Solve the planning problem
    print("Solving planning problem...")
    assignments = service.solve()
    
    if not assignments:
        print("No valid solution found!")
        return
    
    # Print assignments
    print(f"\nFound {len(assignments)} assignments:")
    for assignment in assignments:
        print(f"{assignment['duty_code']} ({assignment['date']} {assignment['start_time']}-{assignment['end_time']}): "
              f"{', '.join(assignment['assigned_employees'])}")
    
    # Print workload distribution
    print("\nWorkload distribution:")
    workload = service.get_workload_distribution()
    for emp_name, hours in sorted(workload.items()):
        print(f"{emp_name}: {hours:.1f} hours")

def run_with_direct_config():
    """Run the resource planning example using a direct configuration."""
    print("\n=== Using direct configuration ===")
    
    # Load a sample configuration
    config_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'configurations', 'oge.json')
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Validate the configuration
    validation_result = ResourcePlanningService.validate_configuration(config)
    if not validation_result["valid"]:
        print("Configuration validation failed:")
        for error in validation_result["errors"]:
            print(f"  - {error}")
        return
    
    print("Configuration validation successful")
    
    # Create a service instance with the direct configuration
    service = ResourcePlanningService(config)
    
    # Get configuration information
    config_info = service.get_configuration_info()
    print(f"Configuration: {config_info['name']}")
    print(f"Description: {config_info['description']}")
    print(f"Period: {config_info['start_date']} to {config_info['end_date']}")
    print(f"Employees: {config_info['num_employees']}")
    print(f"Duties: {config_info['num_duties']}")
    print()
    
    # Solve the planning problem
    print("Solving planning problem...")
    assignments = service.solve()
    
    if not assignments:
        print("No valid solution found!")
        return
    
    # Print assignments
    print(f"\nFound {len(assignments)} assignments:")
    for assignment in assignments:
        print(f"{assignment['duty_code']} ({assignment['date']} {assignment['start_time']}-{assignment['end_time']}): "
              f"{', '.join(assignment['assigned_employees'])}")
    
    # Print workload distribution
    print("\nWorkload distribution:")
    workload = service.get_workload_distribution()
    for emp_name, hours in sorted(workload.items()):
        print(f"{emp_name}: {hours:.1f} hours")

def main():
    """Run the resource planning examples."""
    # Example 1: Using configuration by name
    run_with_config_name()
    
    # Example 2: Using direct configuration
    run_with_direct_config()
    
    # Example of getting assignments for a specific employee
    print("\n=== Example: Employee assignments ===")
    service = ResourcePlanningService("oge")
    print("Assignments for Anna Schmidt:")
    emp_assignments = service.get_employee_assignments(0)  # Anna's ID is 0
    for assignment in emp_assignments:
        print(f"{assignment['duty_code']} ({assignment['date']} {assignment['start_time']}-{assignment['end_time']})")
    
    # Example of getting assignments for a specific duty code
    print("\n=== Example: Duty assignments ===")
    print("All DIS assignments:")
    duty_assignments = service.get_duty_assignments("DIS")
    for assignment in duty_assignments:
        print(f"{assignment['date']} {assignment['start_time']}-{assignment['end_time']}: "
              f"{', '.join(assignment['assigned_employees'])}")

if __name__ == "__main__":
    main() 