# Resource Planner API

A RESTful API for solving resource planning problems using constraint-based optimization, built with Google OR-Tools.

## Table of Contents

- [Features](#features)
- [API Endpoints](#api-endpoints)
- [Setup](#setup)
- [How to Run](#how-to-run)
- [How to Execute Tests](#how-to-execute-tests)
- [Configuration](#configuration)
  - [On-Disk Configuration Files](#on-disk-configuration-files)
  - [API Input Configuration](#api-input-configuration)

## Features

- Solve resource planning problems with various constraints (e.g., max work days in a row, rest time, required employees).
- Support for loading configurations from files or receiving them directly via API.
- Validation of solutions against defined constraints.
- Debugging capabilities to inspect solver inputs and outputs.

## API Endpoints

Base Path: `/api/resource-planner`

### List Available Configurations

-   **Endpoint:** `GET /configurations`
-   **Description:** Returns a list of names of pre-defined configurations available in the `resource_planner/data/configurations/` directory.
-   **Response:**
    ```json
    [
      "config_name_1",
      "config_name_2"
    ]
    ```

### Solve Resource Planning Problem

-   **Endpoint:** `POST /solve`
-   **Description:** Solves a resource planning problem. The request body can be either:
    1.  A JSON object specifying the name of a pre-defined configuration:
        ```json
        {"config_name": "name_from_get_configurations"}
        ```
    2.  A complete configuration JSON object (see [API Input Configuration](#api-input-configuration) section for format).
-   **Response (Success - 200 OK):**
    ```json
    {
      "date": "YYYY-MM-DD",
      "start_time": "HH:MM:SS",
      "end_time": "HH:MM:SS",
      "duration_seconds": 1.234,
      "status": "OPTIMAL", // Or other statuses like FEASIBLE, INFEASIBLE, etc.
      "assignments": [
        {
          "duty_id": 0,
          "duty_code": "DUTY_CODE",
          "date": "YYYY-MM-DD",
          "start_time": "HH:MM",
          "end_time": "HH:MM",
          "employees": [
            {"employee_id": 0, "employee_name": "Employee Name"}
          ]
        }
        // ... more assignments
      ]
    }
    ```
-   **Response (Error - e.g., 400 Bad Request, 404 Not Found):**
    ```json
    {
      "error": "Error message describing the issue"
    }
    ```

### Validate Solution (Example - if you implement it)

-   **Endpoint:** `POST /validate-solution` (This is an example, actual validation is part of the solver)
-   **Description:** This endpoint is illustrative. The current system validates constraints during the solve process. If you were to expose validation separately, it might look like this.
-   **Request Body:** Full solution JSON (similar to the `/solve` response).
-   **Response:** Validation results.

## Setup

This application uses the same project-level setup as described in the main [README.md](../README.md).
Ensure you have completed the following steps from the main README:
1.  Cloned the repository.
2.  Created and activated a virtual environment.
3.  Installed dependencies using `uv sync`.

No additional setup steps are required specifically for the Resource Planner API if the main project setup is complete.

## How to Run

There are a couple of ways to run the Resource Planner API:

### 1. Using the Python script directly (via Flask's development server)

```bash
python resource_planner/src/run_api.py
```
This will start the Flask development server, typically on `http://127.0.0.1:5000/`.

To run with Flask debugging enabled (for auto-reload and an interactive debugger in the browser for errors):

-   **Windows (PowerShell):**
    ```powershell
    $env:FLASK_ENV="development"
    python resource_planner/src/run_api.py
    ```
-   **macOS/Linux:**
    ```bash
    FLASK_ENV=development python resource_planner/src/run_api.py
    ```

### 2. Using VS Code Launch Configuration

The project includes a pre-configured `launch.json` for VS Code (`.vscode/launch.json`).
1.  Open the project in VS Code.
2.  Go to the "Run and Debug" panel (Ctrl+Shift+D).
3.  Select the **"Python: Resource Planner API"** configuration from the dropdown.
4.  Press F5 or click the green play button to start the API with debugging capabilities.
    This configuration sets `FLASK_APP` and `FLASK_ENV` appropriately.

## How to Execute Tests

Unit tests for the Resource Planner API are written using `pytest`.
To run all tests for this application:

```bash
python -m pytest resource_planner/tests/ -v
```

This command should be run from the root of the project directory.
The `-v` flag provides verbose output.

## Configuration

The Resource Planner API uses two main types of configurations:

### 1. On-Disk Configuration Files

These files are stored in the `resource_planner/data/configurations/` directory and represent pre-defined, reusable problem scenarios for the resource planner. When using the `/solve` API endpoint with a `config_name`, the API loads the corresponding JSON file from this directory.

**Example (`test_l1.json`):**

```json
{
  "name": "Test Level 1",
  "description": "A very simple test with 2 employees and duty",
  "start_date": "2025-05-01",
  "end_date": "2025-05-07",
  "employees": [
    {
      "id": 0,
      "name": "Anna Schmidt",
      "max_days_in_a_row": 6,
      "off_days": ["2025-05-03"],
      "max_hours_per_day": 8,
      "max_hours_in_period": 40,
      "work_percentage": 100
    },
    {
      "id": 1,
      "name": "Ben Weber",
      "max_days_in_a_row": 6,
      "off_days": ["2025-05-06"],
      "max_hours_per_day": 8,
      "max_hours_in_period": 40,
      "work_percentage": 100
    }
  ],
  "duties": [
    {
      "code": "DIS",
      "required_employees": 1,
      "start_time": "04:00",
      "end_time": "13:00"
    }
  ]
}
```

**Property Documentation:**

*   `name` (string): <!-- TODO: Describe property -->
*   `description` (string): <!-- TODO: Describe property -->
*   `start_date` (string, `YYYY-MM-DD`): <!-- TODO: Describe property -->
*   `end_date` (string, `YYYY-MM-DD`): <!-- TODO: Describe property -->
*   `employees` (array of objects):
    *   `id` (integer): <!-- TODO: Describe property -->
    *   `name` (string): <!-- TODO: Describe property -->
    *   `max_days_in_a_row` (integer): <!-- TODO: Describe property -->
    *   `off_days` (array of strings, `YYYY-MM-DD`): <!-- TODO: Describe property -->
    *   `max_hours_per_day` (integer): <!-- TODO: Describe property -->
    *   `max_hours_in_period` (integer): <!-- TODO: Describe property -->
    *   `work_percentage` (integer): <!-- TODO: Describe property -->
*   `duties` (array of objects):
    *   `code` (string): <!-- TODO: Describe property -->
    *   `required_employees` (integer): <!-- TODO: Describe property -->
    *   `start_time` (string, `HH:MM`): <!-- TODO: Describe property -->
    *   `end_time` (string, `HH:MM`): <!-- TODO: Describe property -->

### 2. API Input Configuration

This is the configuration format expected by the `POST /api/resource-planner/solve` endpoint when you provide the full configuration details directly in the request body, instead of just a `config_name`.

This format is very similar to the on-disk configuration but may include additional fields that are dynamically generated or pre-processed by the `ConfigLoader` before being passed to the solver, such as specific duty dates and calculated working minutes. The files in `resource_planner/data/debug/input_*.json` reflect this fully processed structure that is fed to the solver.

**Example (based on `input_20250509_094549.json`):**

```json
{
  "name": "Test Max Working Hours",
  "description": "A very simple test with 3 employees and a duty to test max working time per period",
  "start_date": "2025-05-01",
  "end_date": "2025-05-05",
  "employees": [
    {
      "id": 0,
      "name": "Anna Schmidt",
      "max_days_in_a_row": 6,
      "off_days": [],
      "max_hours_per_day": 8,
      "max_hours_in_period": 8,
      "work_percentage": 20
    },
    {
      "id": 1,
      "name": "Ben Weber",
      "max_days_in_a_row": 6,
      "off_days": [],
      "max_hours_per_day": 8,
      "max_hours_in_period": 100,
      "work_percentage": 32
    }
  ],
  "duties": [
    {
      "code": "DIS",
      "required_employees": 1,
      "start_time": "08:00",
      "end_time": "16:00",
      "date": "2025-05-01",
      "id": 0,
      "working_minutes": 480
    },
    {
      "code": "DIS",
      "required_employees": 1,
      "start_time": "08:00",
      "end_time": "16:00",
      "date": "2025-05-02",
      "id": 1,
      "working_minutes": 480
    }
    // ... more duties for other dates up to end_date
  ]
}
```

**Property Documentation:**

*   `name` (string): <!-- TODO: Describe property -->
*   `description` (string): <!-- TODO: Describe property -->
*   `start_date` (string, `YYYY-MM-DD`): <!-- TODO: Describe property -->
*   `end_date` (string, `YYYY-MM-DD`): <!-- TODO: Describe property -->
*   `employees` (array of objects):
    *   `id` (integer): <!-- TODO: Describe property -->
    *   `name` (string): <!-- TODO: Describe property -->
    *   `max_days_in_a_row` (integer): <!-- TODO: Describe property -->
    *   `off_days` (array of strings, `YYYY-MM-DD`): <!-- TODO: Describe property -->
    *   `max_hours_per_day` (integer): <!-- TODO: Describe property -->
    *   `max_hours_in_period` (integer): <!-- TODO: Describe property -->
    *   `work_percentage` (integer): <!-- TODO: Describe property -->
*   `duties` (array of objects): These represent specific duty instances for each day within the date range.
    *   `code` (string): <!-- TODO: Describe property -->
    *   `required_employees` (integer): <!-- TODO: Describe property -->
    *   `start_time` (string, `HH:MM`): <!-- TODO: Describe property -->
    *   `end_time` (string, `HH:MM`): <!-- TODO: Describe property -->
    *   `date` (string, `YYYY-MM-DD`): <!-- TODO: Describe property (date of this specific duty instance) -->
    *   `id` (integer): <!-- TODO: Describe property (unique ID for this duty instance) -->
    *   `working_minutes` (integer): <!-- TODO: Describe property (calculated duration) --> 