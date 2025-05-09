import pytest
from resource_planner.src.constraints import WorkloadBalanceConstraint

class TestWorkloadBalanceConstraint:
    """Tests for WorkloadBalanceConstraint validation."""
    
    @pytest.fixture
    def valid_assignments(self):
        """Valid assignments with balanced workload among employees."""
        return [
            # Employee 0 works 8 hours
            {
                "duty_id": 0,
                "date": "2025-05-01",
                "start_time": "08:00",
                "end_time": "16:00",  # 8 hours
                "employees": [{"employee_id": 0, "employee_name": "Anna Schmidt"}]
            },
            # Employee 1 works 8.5 hours
            {
                "duty_id": 1,
                "date": "2025-05-01",
                "start_time": "08:00",
                "end_time": "16:30",  # 8.5 hours
                "employees": [{"employee_id": 1, "employee_name": "Ben Weber"}]
            },
            # Employee 2 works 7.5 hours
            {
                "duty_id": 2,
                "date": "2025-05-01",
                "start_time": "09:00",
                "end_time": "16:30",  # 7.5 hours
                "employees": [{"employee_id": 2, "employee_name": "Garry Smith"}]
            },
            # Employee 3 works 8 hours
            {
                "duty_id": 3,
                "date": "2025-05-01",
                "start_time": "09:00",
                "end_time": "17:00",  # 8 hours
                "employees": [{"employee_id": 3, "employee_name": "Lisa Johnson"}]
            }
            # Max difference: 8.5 - 7.5 = 1 hour (within 20% deviation)
        ]
    
    @pytest.fixture
    def invalid_assignments(self):
        """Invalid assignments with unbalanced workload among employees."""
        return [
            # Employee 0 works 24 hours
            {
                "duty_id": 0,
                "date": "2025-05-01",
                "start_time": "00:00",
                "end_time": "23:59",  # 24 hours
                "employees": [{"employee_id": 0, "employee_name": "Anna Schmidt"}]
            },
            # Employee 1 works 2 hours
            {
                "duty_id": 1,
                "date": "2025-05-01",
                "start_time": "10:00",
                "end_time": "12:00",  # 2 hours
                "employees": [{"employee_id": 1, "employee_name": "Ben Weber"}]
            },
            # Employee 2 works 6 hours
            {
                "duty_id": 2,
                "date": "2025-05-01",
                "start_time": "09:00",
                "end_time": "15:00",  # 6 hours
                "employees": [{"employee_id": 2, "employee_name": "Garry Smith"}]
            },
            # Employee 3 works 4 hours
            {
                "duty_id": 3,
                "date": "2025-05-01",
                "start_time": "10:00",
                "end_time": "14:00",  # 4 hours
                "employees": [{"employee_id": 3, "employee_name": "Lisa Johnson"}]
            }
            # Max difference: 24 - 2 = 22 hours (very unbalanced)
        ]
    
    def test_valid_assignments(self, mock_model, mock_assignments, basic_employees, basic_duties, valid_assignments):
        """Test that valid assignments pass validation."""
        constraint = WorkloadBalanceConstraint(mock_model, mock_assignments, basic_employees, basic_duties, max_deviation_percent=20)
        assert constraint.validate(valid_assignments)
    
    def test_invalid_assignments(self, mock_model, mock_assignments, basic_employees, basic_duties, invalid_assignments):
        """Test that invalid assignments fail validation."""
        constraint = WorkloadBalanceConstraint(mock_model, mock_assignments, basic_employees, basic_duties, max_deviation_percent=20)
        assert not constraint.validate(invalid_assignments) 