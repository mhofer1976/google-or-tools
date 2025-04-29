#!/usr/bin/env python
"""
Example client script demonstrating how to use the Resource Planner API.
"""

import requests
import json
import sys
import os

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# API base URL
API_BASE_URL = "http://localhost:5000/api/resource-planner"

def list_configurations():
    """List all available configurations."""
    response = requests.get(f"{API_BASE_URL}/configurations")
    if response.status_code == 200:
        configs = response.json()["configurations"]
        print(f"Available configurations: {', '.join(configs)}")
        return configs
    else:
        print(f"Error: {response.json()['error']}")
        return []

def solve_with_config_name(config_name):
    """Solve the resource planning problem using a configuration name."""
    print(f"\nSolving with configuration: {config_name}")
    
    response = requests.post(
        f"{API_BASE_URL}/solve",
        json={"config_name": config_name}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"Solution found with {len(result['assignments'])} assignments")
        
        # Print validation results
        print("\nValidation results:")
        for constraint, is_valid in result["validation_results"].items():
            print(f"  {constraint}: {'Valid' if is_valid else 'Invalid'}")
        
        # Print assignments
        print("\nAssignments:")
        for assignment in result["assignments"]:
            print(f"  {assignment['date']} - {assignment['duty_code']} "
                  f"({assignment['start_time']}-{assignment['end_time']}): "
              f"Employee {assignment['employee_id']} ({assignment['employee_name']})")
    else:
        print(f"Error: {response.json()['error']}")

def solve_with_direct_config():
    """Solve the resource planning problem using a direct configuration."""
    print("\nSolving with direct configuration")
    
    # Load a sample configuration
    config_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'configurations', 'oge.json')
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Validate the configuration first
    response = requests.post(
        f"{API_BASE_URL}/validate-config",
        json=config
    )
    
    if response.status_code == 200:
        validation_result = response.json()
        if validation_result["valid"]:
            print("Configuration validation successful")
        else:
            print("Configuration validation failed:")
            for error in validation_result["errors"]:
                print(f"  - {error}")
            return
    
    # Solve with the configuration
    response = requests.post(
        f"{API_BASE_URL}/solve",
        json=config
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"Solution found with {len(result['assignments'])} assignments")
        
        # Print validation results
        print("\nValidation results:")
        for constraint, is_valid in result["validation_results"].items():
            print(f"  {constraint}: {'Valid' if is_valid else 'Invalid'}")
        
        # Print assignments
        print("\nAssignments:")
        for assignment in result["assignments"]:
            print(f"  {assignment['date']} - {assignment['duty_code']} "
                  f"({assignment['start_time']}-{assignment['end_time']}): "
              f"Employee {assignment['employee_id']} ({assignment['employee_name']})")
    else:
        print(f"Error: {response.json()['error']}")

def main():
    """Run the API client examples."""
    # List available configurations
    configs = list_configurations()
    
    if configs:
        # Example 1: Solve with configuration name
        solve_with_config_name(configs[0])
        
        # Example 2: Solve with direct configuration
        solve_with_direct_config()

if __name__ == "__main__":
    main() 