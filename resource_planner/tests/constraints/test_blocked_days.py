import pytest
from resource_planner.src.constraints import BlockedDaysConstraint

class TestBlockedDaysConstraint:
    """Tests for BlockedDaysConstraint validation."""
    
    @pytest.fixture
    def employees_with_blocked_days(self, basic_employees):
        """Create employees with blocked_days."""
        employees = [emp.copy() for emp in basic_employees]
        employees[0]["blocked_days"] = ["2025-05-01", "2025-05-02"]
        employees[1]["blocked_days"] = ["2025-05-03", "2025-05-04"]
        return employees
    
    @pytest.fixture
    def valid_assignments(self):
        """Valid assignments where employees don't work on their blocked days."""
        return [
            {
                "duty_id": 0,
                "date": "2025-05-01",
                "start_time": "04:00",
                "end_time": "13:00",
                "employees": [
                    # Employee 0 is blocked on May 1
                    {"employee_id": 2, "employee_name": "Garry Smith"},
                    {"employee_id": 3, "employee_name": "Lisa Johnson"}
                ]
            },
            {
                "duty_id": 1,
                "date": "2025-05-03",
                "start_time": "04:00",
                "end_time": "13:00",
                "employees": [
                    # Employee 1 is blocked on May 3
                    {"employee_id": 0, "employee_name": "Anna Schmidt"},
                    {"employee_id": 2, "employee_name": "Garry Smith"}
                ]
            }
        ]
    
    @pytest.fixture
    def invalid_assignments(self):
        """Invalid assignments where employees work on their blocked days."""
        return [
            {
                "duty_id": 0,
                "date": "2025-05-01",
                "start_time": "04:00",
                "end_time": "13:00",
                "employees": [
                    # Employee 0 is assigned but is blocked on May 1
                    {"employee_id": 0, "employee_name": "Anna Schmidt"},
                    {"employee_id": 2, "employee_name": "Garry Smith"}
                ]
            },
            {
                "duty_id": 1,
                "date": "2025-05-03",
                "start_time": "04:00",
                "end_time": "13:00",
                "employees": [
                    # Employee 1 is assigned but is blocked on May 3
                    {"employee_id": 1, "employee_name": "Ben Weber"},
                    {"employee_id": 2, "employee_name": "Garry Smith"}
                ]
            }
        ]
    
    def test_valid_assignments(self, mock_model, mock_assignments, employees_with_blocked_days, basic_duties, valid_assignments):
        """Test that valid assignments pass validation."""
        constraint = BlockedDaysConstraint(mock_model, mock_assignments, employees_with_blocked_days, basic_duties)
        assert constraint.validate(valid_assignments)
    
    def test_invalid_assignments(self, mock_model, mock_assignments, employees_with_blocked_days, basic_duties, invalid_assignments):
        """Test that invalid assignments fail validation."""
        constraint = BlockedDaysConstraint(mock_model, mock_assignments, employees_with_blocked_days, basic_duties)
        assert not constraint.validate(invalid_assignments) 