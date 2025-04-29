# Resource Planner API

A RESTful API for solving resource planning problems using constraint-based optimization.

## Features

- Solve resource planning problems with various constraints
- Support for multiple configuration formats
- Validation of solutions against constraints
- Easy integration with other systems

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

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the API server:
   ```
   python run_api.py
   ```

3. The API will be available at `http://localhost:5000`

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
