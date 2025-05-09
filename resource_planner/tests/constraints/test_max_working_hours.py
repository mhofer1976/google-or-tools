import pytest
from resource_planner.src.constraints import MaxWorkingHoursInPeriodConstraints

class TestMaxWorkingHoursConstraint:
    """Tests for MaxWorkingHoursInPeriodConstraints validation."""
    
    @pytest.fixture
    def valid_assignments(self):
        """Valid assignments where employees don't exceed max working hours."""
        return [
            # Employee 0 works 9 hours on 2025-05-01
            {
                "duty_id": 0,
                "date": "2025-05-01",
                "start_time": "04:00",
                "end_time": "13:00",  # 9 hours
                "employees": [{"employee_id": 0, "employee_name": "Anna Schmidt"}]
            },
            # Employee 0 works 8 hours on 2025-05-02
            {
                "duty_id": 1,
                "date": "2025-05-02",
                "start_time": "08:00",
                "end_time": "16:00",  # 8 hours
                "employees": [{"employee_id": 0, "employee_name": "Anna Schmidt"}]
            },
            # Employee 0 works 8 hours on 2025-05-03
            {
                "duty_id": 2,
                "date": "2025-05-03",
                "start_time": "09:00",
                "end_time": "17:00",  # 8 hours
                "employees": [{"employee_id": 0, "employee_name": "Anna Schmidt"}]
            }
            # Total: 25 hours (less than max of 40)
        ]
    
    @pytest.fixture
    def invalid_assignments(self, basic_duties):
        """Invalid assignments where employees exceed max working hours."""
        # Create duties that when combined will exceed 40 hours
        assignments = []
        for i in range(5):  # 5 duties of 9 hours each = 45 hours total
            assignments.append({
                "duty_id": i,
                "date": f"2025-05-{i+1:02d}",
                "start_time": "04:00",
                "end_time": "13:00",  # 9 hours
                "employees": [{"employee_id": 0, "employee_name": "Anna Schmidt"}]
            })
        return assignments
    
    def test_valid_assignments(self, mock_model, mock_assignments, basic_employees, basic_duties, valid_assignments):
        """Test that valid assignments pass validation."""
        constraint = MaxWorkingHoursInPeriodConstraints(mock_model, mock_assignments, basic_employees, basic_duties)
        assert constraint.validate(valid_assignments)
    
    def test_invalid_assignments(self, mock_model, mock_assignments, basic_employees, basic_duties, invalid_assignments):
        """Test that invalid assignments fail validation."""
        constraint = MaxWorkingHoursInPeriodConstraints(mock_model, mock_assignments, basic_employees, basic_duties)
        assert not constraint.validate(invalid_assignments) 