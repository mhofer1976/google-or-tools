import pytest
from src.resource_planner.constraints import RequiredEmployeesConstraint

class TestRequiredEmployeesConstraint:
    """Tests for RequiredEmployeesConstraint validation."""
    
    @pytest.fixture
    def duties_with_requirements(self, basic_duties):
        """Modify duties to have required_employees field."""
        duties = [duty.copy() for duty in basic_duties]
        for duty in duties:
            duty["required_employees"] = 2
        return duties
    
    @pytest.fixture
    def valid_assignments(self):
        """Valid assignments where all duties have the required number of employees."""
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
                    {"employee_id": 2, "employee_name": "Garry Smith"},
                    {"employee_id": 3, "employee_name": "Lisa Johnson"}
                ]
            }
        ]
    
    @pytest.fixture
    def invalid_assignments(self):
        """Invalid assignments where duties don't have the required number of employees."""
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
                    # Only one employee assigned instead of required two
                    {"employee_id": 2, "employee_name": "Garry Smith"}
                ]
            }
        ]
    
    def test_valid_assignments(self, mock_model, mock_assignments, basic_employees, duties_with_requirements, valid_assignments):
        """Test that valid assignments pass validation."""
        constraint = RequiredEmployeesConstraint(mock_model, mock_assignments, basic_employees, duties_with_requirements)
        assert constraint.validate(valid_assignments)
    
    def test_invalid_assignments(self, mock_model, mock_assignments, basic_employees, duties_with_requirements, invalid_assignments):
        """Test that invalid assignments fail validation."""
        constraint = RequiredEmployeesConstraint(mock_model, mock_assignments, basic_employees, duties_with_requirements)
        assert not constraint.validate(invalid_assignments) 