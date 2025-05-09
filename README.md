# Google OR-Tools Examples and Applications

A collection of practical examples and applications built using Google OR-Tools for solving various optimization problems.

## Overview

This repository contains multiple modules and applications that demonstrate how to use Google OR-Tools for different types of optimization problems. Each module is designed to be self-contained and can be used independently.

## Project Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-name>
    ```

2.  **Create and activate a virtual environment:**
    It is highly recommended to use a virtual environment to manage project dependencies.
    ```bash
    # Using Python's built-in venv
    python -m venv .venv
    # Activate the environment
    # On Windows
    .venv\Scripts\activate
    # On macOS/Linux
    source .venv/bin/activate
    ```

3.  **Install dependencies using `uv`:**
    This project uses `uv` for fast dependency management.
    ```bash
    # Install uv if you haven't already (ensure pip is from your activated venv)
    pip install uv

    # Sync dependencies from pyproject.toml
    uv sync
    ```

## Available Applications

Currently, the primary application available is:

*   **Resource Planner API**: A RESTful API for solving resource planning problems using constraint-based optimization.
    *   For detailed information on the Resource Planner API, including how to run it, its API endpoints, configuration details, and how to run its specific tests, please see its dedicated [README.md](./resource_planner/README.md).
    *   **Interactive Testing:** A Jupyter notebook (`resource_planner/notebooks/resource_planning.ipynb`) is provided to interactively test the API. This notebook demonstrates how to list available configurations and solve resource planning problems using the API. Ensure the API is running before executing the notebook cells.

*(More applications may be added in the future.)*

## General Debugging

Here are general ways to debug applications in this project:

### 1. Using Python's Built-in Debugger (pdb)

1.  Identify the main script of the application you want to debug.
2.  You can insert `import pdb; pdb.set_trace()` in your code where you want to start debugging.
3.  Run the application script. The debugger will pause at your breakpoint.
    *   `n` - Step to the next line
    *   `s` - Step into a function
    *   `c` - Continue execution
    *   `p variable` - Print a variable's value
    *   `l` - Show the current location in the code
    *   `q` - Quit the debugger

### 2. Using VS Code's Debugger (Recommended)

1.  Ensure you have the Python extension for VS Code installed.
2.  Open the project folder in VS Code.
3.  Configure `launch.json` in the `.vscode` folder for the specific application you want to debug. An example for the Resource Planner API is already provided.
    General structure for a Flask app:
    ```json
    {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Python: Flask App",
                "type": "debugpy",
                "request": "launch",
                "module": "flask",
                "env": {
                    "FLASK_APP": "your_app_module.run_api_or_app_file", // Adjust path
                    "FLASK_ENV": "development"
                },
                "args": [
                    "run",
                    "--reload" // Enable auto-reload for development. Note: If you experience issues with the VS Code debugger, try --no-reload.
                ],
                "jinja": true, // If using Jinja templates
                "justMyCode": true, // Set to false to step into library code
                "cwd": "${workspaceFolder}"
            }
        ]
    }
    ```
4.  Select the desired configuration from the "Run and Debug" panel and press F5 to start debugging.

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.
