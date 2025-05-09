import pytest
from resource_planner.src.constraints import OneDutyPerDayConstraint

class TestOneDutyPerDayConstraint:
    """Tests for OneDutyPerDayConstraint validation."""
    
    @pytest.fixture
    def valid_assignments(self):
        """Valid assignments where each employee has at most one duty per day."""
        return [
            {
                "duty_id": 0,
                "date": "2025-05-01",
                "start_time": "04:00",
                "end_time": "13:00",
                "employees": [
                    {"employee_id": 0, "employee_name": "Anna Schmidt"},
                    {"employee_id": 1, "employee_name": "Ben Weber"}
                ]
            },
            {
                "duty_id": 1,
                "date": "2025-05-02",
                "start_time": "04:00",
                "end_time": "13:00",
                "employees": [
                    {"employee_id": 0, "employee_name": "Anna Schmidt"},
                    {"employee_id": 2, "employee_name": "Garry Smith"}
                ]
            },
            {
                "duty_id": 2,
                "date": "2025-05-01",
                "start_time": "14:00",
                "end_time": "23:00",
                "employees": [
                    {"employee_id": 2, "employee_name": "Garry Smith"},
                    {"employee_id": 3, "employee_name": "Lisa Johnson"}
                ]
            }
        ]
    
    @pytest.fixture
    def invalid_assignments(self):
        """Invalid assignments where an employee has multiple duties on the same day."""
        return [
            {
                "duty_id": 0,
                "date": "2025-05-01",
                "start_time": "04:00",
                "end_time": "13:00",
                "employees": [
                    {"employee_id": 0, "employee_name": "Anna Schmidt"},
                    {"employee_id": 1, "employee_name": "Ben Weber"}
                ]
            },
            {
                "duty_id": 1,
                "date": "2025-05-01",  # Same day as duty_id 0
                "start_time": "14:00",
                "end_time": "23:00",
                "employees": [
                    {"employee_id": 0, "employee_name": "Anna Schmidt"},  # Same employee as in duty_id 0
                    {"employee_id": 2, "employee_name": "Garry Smith"}
                ]
            }
        ]
    
    def test_valid_assignments(self, mock_model, mock_assignments, basic_employees, basic_duties, valid_assignments):
        """Test that valid assignments pass validation."""
        constraint = OneDutyPerDayConstraint(mock_model, mock_assignments, basic_employees, basic_duties)
        assert constraint.validate(valid_assignments)
    
    def test_invalid_assignments(self, mock_model, mock_assignments, basic_employees, basic_duties, invalid_assignments):
        """Test that invalid assignments fail validation."""
        constraint = OneDutyPerDayConstraint(mock_model, mock_assignments, basic_employees, basic_duties)
        assert not constraint.validate(invalid_assignments) 