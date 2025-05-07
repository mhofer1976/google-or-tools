# Google OR-Tools Examples and Applications

A collection of practical examples and applications built using Google OR-Tools for solving various optimization problems.

## Overview

This repository contains multiple modules and applications that demonstrate how to use Google OR-Tools for different types of optimization problems. Each module is self-contained and can be used independently.

## Available Modules

### 1. Resource Planner API

A RESTful API for solving resource planning problems using constraint-based optimization.

#### Features
- Solve resource planning problems with various constraints
- Support for multiple configuration formats
- Validation of solutions against constraints
- Easy integration with other systems
- Built-in debugging capabilities

#### API Endpoints

##### List Available Configurations
```
GET /api/resource-planner/configurations
```
Returns a list of available configuration names.

##### Solve Resource Planning Problem
```
POST /api/resource-planner/solve
```
Accepts either:
- A configuration name: `{"config_name": "oge"}`
- A complete configuration JSON

Returns a JSON with valid assignments. Example:
```
{
  "date": "2025-05-07",
  "start_time": "11:30:50",
  "end_time": "11:30:50",
  "duration_seconds": 0.031709,
  "status": "OPTIMAL",
  "assignments": [
    {
      "duty_id": 0,
      "duty_code": "DIS",
      "date": "2025-05-01",
      "start_time": "04:00",
      "end_time": "13:00",
      "employees": [
        {
          "employee_id": 0,
          "employee_name": "Anna Schmidt"
        },
        {
          "employee_id": 1,
          "employee_name": "Ben Weber"
        }
      ]
    }, ...
  ]
}
```

##### Validate Configuration
```
POST /api/resource-planner/validate-config
```
Accepts a configuration JSON and returns validation results.

### 2. TBD
- TBD

## Running the Applications

1. Install dependencies using `uv`:
   ```bash
   # Install uv if you haven't already
   pip install uv

   # Sync dependencies from pyproject.toml
   uv sync
   ```

2. Run the desired application:
   ```bash
   # For Resource Planner API
   python src/resource_planner/run_api.py

   # With debugging enabled (Windows PowerShell)
   $env:DEBUG_API=1
   python src/resource_planner/run_api.py

   # With debugging enabled (Linux/Mac)
   DEBUG_API=1 python src/resource_planner/run_api.py
   ```

## Debugging

Each module includes built-in debugging capabilities. Here are the main ways to debug:

### 1. Using Python's Built-in Debugger (pdb)

1. Start the application with debugging enabled as shown above
2. The debugger will pause at breakpoints. Use these commands:
   - `n` - Step to the next line
   - `s` - Step into a function
   - `c` - Continue execution
   - `p variable` - Print a variable's value
   - `l` - Show the current location in the code
   - `q` - Quit the debugger

### 2. Using VS Code's Debugger (Recommended)

1. Create a launch configuration in VS Code.

   ```json
   # For Resource Planner API
   {
       "version": "0.2.0",
       "configurations": [
         {
            "name": "Python: Resource Planner API",
            "type": "debugpy",
            "request": "launch",
            "module": "flask",
            "env": {
                "FLASK_APP": "src.resource_planner.run_api",
                "FLASK_ENV": "development",
                "DEBUG_API": "1"
            },
            "args": [
                "run",
                "--debug",
                "--reload"
            ],
            "jinja": true,
            "justMyCode": false,
            "cwd": "${workspaceFolder}"
         }
       ]
   }
   ```


3. Choose the configuration and start debugging (F5)

## Configuration Formats

Each module has its own configuration format.

### Resource Planner Configuration Format

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

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
