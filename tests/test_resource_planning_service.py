import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from src.resource_planning_service import ResourcePlanningService

# Sample test data
SAMPLE_CONFIG = {
    "name": "Test Config",
    "description": "Test configuration",
    "start_date": "2025-05-01",
    "end_date": "2025-05-31",
    "employees": [
        {
            "id": 1,
            "name": "Test Employee",
            "max_days_in_a_row": 5,
            "off_days": ["2025-05-03", "2025-05-04"],
            "max_hours_per_day": 8,
            "max_hours_in_period": 160,
            "work_percentage": 100
        }
    ],
    "duties": [
        {
            "code": "TEST",
            "required_employees": 1,
            "start_time": "08:00",
            "end_time": "16:00"
        }
    ]
}

@pytest.fixture
def mock_config_loader():
    """Fixture that provides a mocked ConfigLoader."""
    with patch('src.resource_planning_service.ConfigLoader') as mock:
        loader_instance = mock.return_value
        loader_instance.load_configuration.return_value = SAMPLE_CONFIG
        yield loader_instance

@pytest.fixture
def mock_resource_planner():
    """Fixture that provides a mocked ResourcePlanner."""
    with patch('src.resource_planning_service.ResourcePlanner') as mock:
        planner_instance = mock.return_value
        yield planner_instance

@pytest.fixture
def service(mock_config_loader, mock_resource_planner):
    """Fixture that provides a ResourcePlanningService instance with mocked dependencies."""
    return ResourcePlanningService("test_config")

def test_initialization(service, mock_config_loader, mock_resource_planner):
    """Test that the service initializes correctly."""
    # Check that ConfigLoader was initialized and configuration was loaded
    mock_config_loader.load_configuration.assert_called_once_with("test_config")
    
    # Check that ResourcePlanner was initialized by verifying its setup methods were called
    mock_resource_planner.add_employee.assert_called()
    mock_resource_planner.add_duty.assert_called()
    mock_resource_planner.setup_model.assert_called_once()

def test_setup_planner(service, mock_resource_planner):
    """Test that the planner is set up correctly with employee and duty data."""
    # Check that add_employee was called with correct parameters
    mock_resource_planner.add_employee.assert_called_once_with(
        1, "Test Employee", 5, ["2025-05-03", "2025-05-04"], 8, 160, 100
    )
    
    # Check that add_duty was called with correct parameters
    mock_resource_planner.add_duty.assert_called_once_with(
        "TEST", 1, "08:00", "16:00"
    )
    
    # Check that setup_model was called
    mock_resource_planner.setup_model.assert_called_once()

def test_solve(service, mock_resource_planner):
    """Test that solve calls the planner's solve method."""
    expected_result = [{"some": "assignment"}]
    mock_resource_planner.solve.return_value = expected_result
    
    result = service.solve()
    
    assert result == expected_result
    mock_resource_planner.solve.assert_called_once()

def test_get_configuration_info(service):
    """Test that get_configuration_info returns correct information."""
    info = service.get_configuration_info()
    
    assert info == {
        "name": "Test Config",
        "description": "Test configuration",
        "start_date": "2025-05-01",
        "end_date": "2025-05-31",
        "num_employees": 1,
        "num_duties": 1
    }

def test_get_employee_assignments(service, mock_config_loader, mock_resource_planner):
    """Test that get_employee_assignments returns correct assignments."""
    # Set up mock returns
    mock_config_loader.get_employee_by_id.return_value = SAMPLE_CONFIG["employees"][0]
    expected_assignments = [{"assigned_employees": ["Test Employee"]}]
    mock_resource_planner.solve.return_value = expected_assignments
    
    # Call the method
    result = service.get_employee_assignments(1)
    
    # Check results
    assert result == expected_assignments
    mock_config_loader.get_employee_by_id.assert_called_once_with(SAMPLE_CONFIG, 1)
    mock_resource_planner.solve.assert_called_once()

def test_get_employee_assignments_not_found(service, mock_config_loader):
    """Test that get_employee_assignments returns empty list for non-existent employee."""
    mock_config_loader.get_employee_by_id.return_value = None
    
    result = service.get_employee_assignments(999)
    
    assert result == []
    mock_config_loader.get_employee_by_id.assert_called_once_with(SAMPLE_CONFIG, 999)

def test_get_duty_assignments(service, mock_resource_planner):
    """Test that get_duty_assignments returns correct assignments."""
    expected_assignments = [{"duty_code": "TEST"}]
    mock_resource_planner.solve.return_value = expected_assignments
    
    result = service.get_duty_assignments("TEST")
    
    assert result == expected_assignments
    mock_resource_planner.solve.assert_called_once()

def test_get_assignments_by_date(service, mock_resource_planner):
    """Test that get_assignments_by_date returns correct assignments."""
    expected_assignments = [{"date": "2025-05-01"}]
    mock_resource_planner.solve.return_value = expected_assignments
    
    result = service.get_assignments_by_date("2025-05-01")
    
    assert result == expected_assignments
    mock_resource_planner.solve.assert_called_once()

def test_calculate_duty_hours_regular(service):
    """Test that _calculate_duty_hours calculates regular duty hours correctly."""
    hours = service._calculate_duty_hours("08:00", "16:00")
    assert hours == 8.0

def test_calculate_duty_hours_overnight(service):
    """Test that _calculate_duty_hours calculates overnight duty hours correctly."""
    hours = service._calculate_duty_hours("21:00", "03:00")
    assert hours == 6.0

def test_calculate_duty_hours_late_night(service):
    """Test that _calculate_duty_hours calculates late night duty hours correctly."""
    hours = service._calculate_duty_hours("23:00", "01:00")
    assert hours == 2.0

def test_get_workload_distribution(service, mock_resource_planner, mock_config_loader):
    """Test that get_workload_distribution calculates workload correctly."""
    # Set up mock assignments with duty_id
    mock_resource_planner.solve.return_value = [
        {
            "assigned_employees": ["Test Employee"],
            "start_time": "08:00",
            "end_time": "16:00",
            "duty_id": 0
        },
        {
            "assigned_employees": ["Test Employee"],
            "start_time": "21:00",
            "end_time": "03:00",
            "duty_id": 1
        }
    ]
    
    # Mock the get_duty_by_id method to return duties with working_hours
    mock_config_loader.get_duty_by_id.side_effect = [
        {"working_hours": 8.0},  # For duty_id 0
        {"working_hours": 6.0}   # For duty_id 1
    ]
    
    # Call the method
    workload = service.get_workload_distribution()
    
    # Check results (8 hours + 6 hours = 14 hours)
    assert workload == {"Test Employee": 14.0}
    mock_resource_planner.solve.assert_called_once()
    assert mock_config_loader.get_duty_by_id.call_count == 2
    mock_config_loader.get_duty_by_id.assert_any_call(SAMPLE_CONFIG, 0)
    mock_config_loader.get_duty_by_id.assert_any_call(SAMPLE_CONFIG, 1) 