import pytest
from datetime import datetime, timedelta

class MockModel:
    """Mock CP-SAT model for testing."""
    def Add(self, constraint):
        pass

# Test fixtures
@pytest.fixture
def mock_model():
    """Mock CP-SAT model for testing."""
    return MockModel()

@pytest.fixture
def mock_assignments():
    """Mock assignments dictionary for testing."""
    return {}

@pytest.fixture
def basic_employees():
    """Basic employee data for testing."""
    return [
        {"id": 0, "name": "Anna Schmidt", "max_days_in_a_row": 3, "max_hours_in_period": 40, "blocked_days": []},
        {"id": 1, "name": "Ben Weber", "max_days_in_a_row": 3, "max_hours_in_period": 40, "blocked_days": []},
        {"id": 2, "name": "Garry Smith", "max_days_in_a_row": 3, "max_hours_in_period": 40, "blocked_days": []},
        {"id": 3, "name": "Lisa Johnson", "max_days_in_a_row": 3, "max_hours_in_period": 40, "blocked_days": []}
    ]

@pytest.fixture
def basic_duties():
    """Basic duty data for testing."""
    return [
        {
            "id": i,
            "code": "DIS",
            "date": f"2025-05-{i+1:02d}",
            "start_time": "04:00",
            "end_time": "13:00",
            "working_minutes": 540,  # 9 hours in minutes
            "required_employees": 2  # Add required_employees field
        }
        for i in range(14)
    ] 