# Resource Planner API

A RESTful API for solving resource planning problems using constraint-based optimization.

## Features

- Solve resource planning problems with various constraints
- Support for multiple configuration formats
- Validation of solutions against constraints
- Easy integration with other systems
- Built-in debugging capabilities

## API Endpoints

### 1. List Available Configurations

```
GET /api/resource-planner/configurations
```

Returns a list of available configuration names.

### 2. Solve Resource Planning Problem

```
POST /api/resource-planner/solve
```

Accepts either:
- A configuration name: `{"config_name": "oge"}`
- A complete configuration JSON

Returns a JSON with valid assignments containing:
- date
- employee_id
- duty_id
- duty_code
- start_time
- end_time
- employee_name

### 3. Validate Configuration

```
POST /api/resource-planner/validate-config
```

Accepts a configuration JSON and returns validation results.

## Running the API

1. Install dependencies using `uv`:
   ```bash
   # Install uv if you haven't already
   pip install uv

   # Sync dependencies from pyproject.toml
   uv sync
   ```

2. Run the API server:
   ```bash
   python run_api.py
   ```

3. The API will be available at `http://localhost:5000`

## Debugging the Solution

The API includes built-in debugging capabilities to help troubleshoot and understand the solution process. There are two main ways to debug:

### 1. Using Python's Built-in Debugger (pdb)

1. Start the API server with debugging enabled:
   ```bash
   # On Windows (PowerShell)
   $env:DEBUG_API=1
   python run_api.py

   # On Linux/Mac
   DEBUG_API=1 python run_api.py
   ```

2. Make a request to the API endpoint:
   ```bash
   curl -X POST http://localhost:5000/api/resource-planner/solve \
     -H "Content-Type: application/json" \
     -d '{"config_name": "oge"}'
   ```

3. The debugger will pause at the breakpoint. Use these commands:
   - `n` - Step to the next line
   - `s` - Step into a function
   - `c` - Continue execution
   - `p variable` - Print a variable's value
   - `l` - Show the current location in the code
   - `q` - Quit the debugger

### 2. Using VS Code's Debugger (Recommended)

1. Create a launch configuration in VS Code:
   ```json
   {
       "version": "0.2.0",
       "configurations": [
           {
               "name": "Python: Flask API",
               "type": "python",
               "request": "launch",
               "module": "flask",
               "env": {
                   "FLASK_APP": "run_api.py",
                   "FLASK_ENV": "development",
                   "DEBUG_API": "1"
               },
               "args": [
                   "run",
                   "--no-debugger",
                   "--no-reload"
               ],
               "jinja": true,
               "justMyCode": false
           }
       ]
   }
   ```

2. Set breakpoints in the code:
   - In `src/api/resource_planner_api.py` for API endpoint debugging
   - In `src/resource_planner.py` for solver debugging
   - In `src/constraints/*.py` for constraint debugging

3. Start debugging using the "Python: Flask API" configuration

4. Make a request to the API endpoint

5. The debugger will pause at your breakpoints, allowing you to:
   - Step through the code
   - Inspect variables
   - Use the debug console
   - Set additional breakpoints

### Debugging Tips

- **Model State**: Use `planner.export_model()` to export the current model state to a JSON file
- **Constraint Validation**: Check `validation_results` to see which constraints are failing
- **Solver Progress**: Enable solver logging with `solver.parameters.log_search_progress = True`
- **Variable Inspection**: Use the debugger to inspect the values of solver variables and constraints

## Example Usage

See `examples/api_client.py` for an example of how to use the API.

## Configuration Format

The configuration should be a JSON object with the following structure:

```json
{
  "name": "Configuration Name",
  "description": "Description of the configuration",
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD",
  "employees": [
    {
      "id": 0,
      "name": "Employee Name",
      "max_days_in_a_row": 6,
      "off_days": ["YYYY-MM-DD", "YYYY-MM-DD"],
      "max_hours_per_day": 8,
      "max_hours_in_period": 160,
      "work_percentage": 100
    }
  ],
  "duties": [
    {
      "code": "DUTY_CODE",
      "required_employees": 2,
      "start_time": "HH:MM",
      "end_time": "HH:MM"
    }
  ]
}
```
