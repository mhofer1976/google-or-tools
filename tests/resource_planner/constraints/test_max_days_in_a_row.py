import pytest
from src.resource_planner.constraints import MaxDaysInARowConstraint

class TestMaxDaysInARowConstraint:
    """Tests for MaxDaysInARowConstraint validation."""
    
    @pytest.fixture
    def valid_assignments(self):
        """Valid assignments where no employee works more than 3 consecutive days."""
        return [
            # Employee 0 works May 1-3 (3 days)
            {
                "duty_id": 0,
                "date": "2025-05-01",
                "start_time": "04:00",
                "end_time": "13:00",
                "employees": [{"employee_id": 0, "employee_name": "Anna Schmidt"}]
            },
            {
                "duty_id": 1,
                "date": "2025-05-02",
                "start_time": "04:00",
                "end_time": "13:00",
                "employees": [{"employee_id": 0, "employee_name": "Anna Schmidt"}]
            },
            {
                "duty_id": 2,
                "date": "2025-05-03",
                "start_time": "04:00",
                "end_time": "13:00",
                "employees": [{"employee_id": 0, "employee_name": "Anna Schmidt"}]
            },
            # Employee 0 has a break on May 4
            {
                "duty_id": 3,
                "date": "2025-05-04",
                "start_time": "04:00",
                "end_time": "13:00",
                "employees": [{"employee_id": 1, "employee_name": "Ben Weber"}]
            },
            # Employee 0 works May 5-7 (3 days)
            {
                "duty_id": 4,
                "date": "2025-05-05",
                "start_time": "04:00",
                "end_time": "13:00",
                "employees": [{"employee_id": 0, "employee_name": "Anna Schmidt"}]
            },
            {
                "duty_id": 5,
                "date": "2025-05-06",
                "start_time": "04:00",
                "end_time": "13:00",
                "employees": [{"employee_id": 0, "employee_name": "Anna Schmidt"}]
            },
            {
                "duty_id": 6,
                "date": "2025-05-07",
                "start_time": "04:00",
                "end_time": "13:00",
                "employees": [{"employee_id": 0, "employee_name": "Anna Schmidt"}]
            }
        ]
    
    @pytest.fixture
    def invalid_assignments(self):
        """Invalid assignments where an employee works more than 3 consecutive days."""
        return [
            # Employee 0 works May 1-5 (5 days, exceeding max of 3)
            {
                "duty_id": 0,
                "date": "2025-05-01",
                "start_time": "04:00",
                "end_time": "13:00",
                "employees": [{"employee_id": 0, "employee_name": "Anna Schmidt"}]
            },
            {
                "duty_id": 1,
                "date": "2025-05-02",
                "start_time": "04:00",
                "end_time": "13:00",
                "employees": [{"employee_id": 0, "employee_name": "Anna Schmidt"}]
            },
            {
                "duty_id": 2,
                "date": "2025-05-03",
                "start_time": "04:00",
                "end_time": "13:00",
                "employees": [{"employee_id": 0, "employee_name": "Anna Schmidt"}]
            },
            {
                "duty_id": 3,
                "date": "2025-05-04",
                "start_time": "04:00",
                "end_time": "13:00",
                "employees": [{"employee_id": 0, "employee_name": "Anna Schmidt"}]
            },
            {
                "duty_id": 4,
                "date": "2025-05-05",
                "start_time": "04:00",
                "end_time": "13:00",
                "employees": [{"employee_id": 0, "employee_name": "Anna Schmidt"}]
            }
        ]
    
    def test_valid_assignments(self, mock_model, mock_assignments, basic_employees, basic_duties, valid_assignments):
        """Test that valid assignments pass validation."""
        constraint = MaxDaysInARowConstraint(mock_model, mock_assignments, basic_employees, basic_duties)
        assert constraint.validate(valid_assignments)
    
    def test_invalid_assignments(self, mock_model, mock_assignments, basic_employees, basic_duties, invalid_assignments):
        """Test that invalid assignments fail validation."""
        constraint = MaxDaysInARowConstraint(mock_model, mock_assignments, basic_employees, basic_duties)
        assert not constraint.validate(invalid_assignments) 