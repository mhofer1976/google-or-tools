import pytest
from resource_planner.src.constraints import RestTimeConstraint

class TestRestTimeConstraint:
    """Tests for RestTimeConstraint validation."""
    
    @pytest.fixture
    def valid_assignments(self):
        """Valid assignments where all employees have sufficient rest time."""
        return [
            # Employee 0 works 2025-05-01 04:00-13:00
            {
                "duty_id": 0,
                "date": "2025-05-01",
                "start_time": "04:00",
                "end_time": "13:00",
                "employees": [{"employee_id": 0, "employee_name": "Anna Schmidt"}]
            },
            # Employee 0 works 2025-05-02 08:00-17:00 (19 hours rest)
            {
                "duty_id": 1,
                "date": "2025-05-02",
                "start_time": "08:00",
                "end_time": "17:00",
                "employees": [{"employee_id": 0, "employee_name": "Anna Schmidt"}]
            },
            # Employee 1 works 2025-05-01 14:00-23:00
            {
                "duty_id": 2,
                "date": "2025-05-01",
                "start_time": "14:00",
                "end_time": "23:00",
                "employees": [{"employee_id": 1, "employee_name": "Ben Weber"}]
            },
            # Employee 1 works 2025-05-02 14:00-23:00 (15 hours rest)
            {
                "duty_id": 3,
                "date": "2025-05-02",
                "start_time": "14:00",
                "end_time": "23:00",
                "employees": [{"employee_id": 1, "employee_name": "Ben Weber"}]
            }
        ]
    
    @pytest.fixture
    def invalid_assignments(self):
        """Invalid assignments where an employee has insufficient rest time."""
        return [
            # Employee 0 works 2025-05-01 04:00-13:00
            {
                "duty_id": 0,
                "date": "2025-05-01",
                "start_time": "04:00",
                "end_time": "13:00",
                "employees": [{"employee_id": 0, "employee_name": "Anna Schmidt"}]
            },
            # Employee 0 works 2025-05-01 22:00-07:00 (only 9 hours rest)
            {
                "duty_id": 1,
                "date": "2025-05-01",
                "start_time": "22:00",
                "end_time": "07:00",
                "employees": [{"employee_id": 0, "employee_name": "Anna Schmidt"}]
            }
        ]
    
    def test_valid_assignments(self, mock_model, mock_assignments, basic_employees, basic_duties, valid_assignments):
        """Test that valid assignments pass validation."""
        constraint = RestTimeConstraint(mock_model, mock_assignments, basic_employees, basic_duties, min_rest_hours=12)
        assert constraint.validate(valid_assignments)
    
    def test_invalid_assignments(self, mock_model, mock_assignments, basic_employees, basic_duties, invalid_assignments):
        """Test that invalid assignments fail validation."""
        constraint = RestTimeConstraint(mock_model, mock_assignments, basic_employees, basic_duties, min_rest_hours=12)
        assert not constraint.validate(invalid_assignments) 