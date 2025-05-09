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
        JSON response containing:
        - date: The date when solving started
        - start_time: When solving started
        - end_time: When solving finished
        - duration_seconds: How long solving took
        - status: The solver status (OPTIMAL, FEASIBLE, or INFEASIBLE)
        - assignments: List of assignments with duty and employee information
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
        result = service.solve()
        
        return jsonify(result)
        
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