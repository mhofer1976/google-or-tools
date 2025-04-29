from typing import Dict, List, Any, Union
import json
from flask import Flask, request, jsonify
from ..resource_planning_service import ResourcePlanningService

app = Flask(__name__)

@app.route('/api/resource-planner/solve', methods=['POST'])
def solve_resource_planning():
    """
    Endpoint to solve a resource planning problem.
    
    Accepts either:
    1. A configuration name in the request body: {"config_name": "oge"}
    2. A complete configuration JSON in the request body
    
    Returns:
        JSON with valid assignments containing at minimum:
        - date
        - employee_id
        - duty_id
        Plus additional helpful attributes
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Check if a configuration name was provided
        if "config_name" in data:
            config_name = data["config_name"]
            service = ResourcePlanningService(config_name)
        else:
            # Use the provided configuration directly
            service = ResourcePlanningService(data)
        
        # Solve the planning problem
        assignments = service.solve()
        
        if not assignments:
            return jsonify({"error": "No valid solution found"}), 404
        
        # Validate the solution against all constraints
        validation_results = service.planner.validate_solution(assignments)
        
        # Check if all constraints are satisfied
        all_valid = all(validation_results.values())
        
        if not all_valid:
            # Filter out assignments that don't meet constraints
            valid_assignments = []
            for assignment in assignments:
                # Check if this assignment is valid according to all constraints
                is_valid = True
                for constraint_name, is_valid_constraint in validation_results.items():
                    if not is_valid_constraint:
                        # We would need more detailed validation per assignment
                        # For now, we'll just return all assignments if any constraint fails
                        is_valid = False
                        break
                
                if is_valid:
                    valid_assignments.append(assignment)
            
            assignments = valid_assignments
        
        # Format the response with the required fields and additional helpful attributes
        formatted_assignments = []
        for assignment in assignments:
            formatted_assignment = {
                "date": assignment["date"],
                "employee_id": assignment["employee_id"],
                "duty_id": assignment["duty_id"],
                # Additional helpful attributes
                "duty_code": assignment["duty_code"],
                "start_time": assignment["start_time"],
                "end_time": assignment["end_time"],
                "employee_name": assignment["employee_name"]
            }
            formatted_assignments.append(formatted_assignment)
        
        return jsonify({
            "success": True,
            "assignments": formatted_assignments,
            "validation_results": validation_results
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/resource-planner/configurations', methods=['GET'])
def list_configurations():
    """
    Endpoint to list all available configurations.
    
    Returns:
        JSON with a list of configuration names
    """
    try:
        configs = ResourcePlanningService.list_available_configurations()
        return jsonify({"configurations": configs})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/resource-planner/validate-config', methods=['POST'])
def validate_configuration():
    """
    Endpoint to validate a configuration.
    
    Accepts a configuration JSON in the request body.
    
    Returns:
        JSON with validation results
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No configuration provided"}), 400
        
        validation_result = ResourcePlanningService.validate_configuration(data)
        return jsonify(validation_result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 