#!/usr/bin/env python
"""
Script to run the Resource Planner API server.
"""

from src.api.resource_planner_api import app

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000) 