import pytest
from src.config_loader import ConfigLoader
from datetime import datetime

def test_valid_configuration():
    """Test that a valid configuration passes validation and expands duties correctly."""
    config = {
        "name": "Test Config",
        "description": "Test configuration",
        "start_date": "2025-05-01",
        "end_date": "2025-05-03",  # 3 days
        "employees": [
            {
                "id": 1,
                "name": "Test Employee",
                "max_days_in_a_row": 5,
                "off_days": ["2025-05-02", "2025-05-03"],  # Changed from "2025-05-04" to be within period
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
    
    loader = ConfigLoader()
    # Should not raise any exceptions
    loader._validate_configuration(config)
    
    # Test duty expansion
    expanded_duties = loader._expand_duties(config)
    
    # Should have 3 duties (1 duty template * 3 days)
    assert len(expanded_duties) == 3
    
    # Check first duty
    assert expanded_duties[0]["date"] == "2025-05-01"
    assert expanded_duties[0]["id"] == 0
    assert expanded_duties[0]["code"] == "TEST"
    assert expanded_duties[0]["working_hours"] == 8.0  # 8 hours for regular shift
    
    # Check second duty
    assert expanded_duties[1]["date"] == "2025-05-02"
    assert expanded_duties[1]["id"] == 1
    assert expanded_duties[1]["code"] == "TEST"
    assert expanded_duties[1]["working_hours"] == 8.0
    
    # Check third duty
    assert expanded_duties[2]["date"] == "2025-05-03"
    assert expanded_duties[2]["id"] == 2
    assert expanded_duties[2]["code"] == "TEST"
    assert expanded_duties[2]["working_hours"] == 8.0

def test_missing_required_keys():
    """Test that missing required keys raise ValueError."""
    config = {
        "name": "Test Config",
        # Missing description
        "start_date": "2025-05-01",
        "end_date": "2025-05-31",
        "employees": [],
        "duties": []
    }
    
    loader = ConfigLoader()
    with pytest.raises(ValueError, match="Configuration must contain the key 'description'"):
        loader._validate_configuration(config)

def test_invalid_date_format():
    """Test that invalid date formats raise ValueError."""
    config = {
        "name": "Test Config",
        "description": "Test configuration",
        "start_date": "2025/05/01",  # Wrong format
        "end_date": "2025-05-31",
        "employees": [],
        "duties": []
    }
    
    loader = ConfigLoader()
    with pytest.raises(ValueError, match="Invalid date format in start_date or end_date"):
        loader._validate_configuration(config)

def test_end_date_before_start_date():
    """Test that end_date before start_date raises ValueError."""
    config = {
        "name": "Test Config",
        "description": "Test configuration",
        "start_date": "2025-05-31",
        "end_date": "2025-05-01",  # Before start_date
        "employees": [],
        "duties": []
    }
    
    loader = ConfigLoader()
    with pytest.raises(ValueError, match="Invalid date format in start_date or end_date"):
        loader._validate_configuration(config)

def test_invalid_employee_fields():
    """Test that invalid employee fields raise ValueError."""
    config = {
        "name": "Test Config",
        "description": "Test configuration",
        "start_date": "2025-05-01",
        "end_date": "2025-05-31",
        "employees": [
            {
                "id": 1,
                "name": "Test Employee",
                # Missing required fields
                "off_days": ["2025-05-03"],
                "work_percentage": 100
            }
        ],
        "duties": []
    }
    
    loader = ConfigLoader()
    with pytest.raises(ValueError, match="Employee must contain the key"):
        loader._validate_configuration(config)

def test_invalid_employee_numeric_fields():
    """Test that invalid numeric employee fields raise ValueError."""
    config = {
        "name": "Test Config",
        "description": "Test configuration",
        "start_date": "2025-05-01",
        "end_date": "2025-05-31",
        "employees": [
            {
                "id": 1,
                "name": "Test Employee",
                "max_days_in_a_row": 0,  # Invalid: must be positive
                "off_days": ["2025-05-03"],
                "max_hours_per_day": 8,
                "max_hours_in_period": 160,
                "work_percentage": 150  # Invalid: must be between 0 and 100
            }
        ],
        "duties": []
    }
    
    loader = ConfigLoader()
    with pytest.raises(ValueError):
        loader._validate_configuration(config)

def test_off_days_outside_period():
    """Test that off_days outside the configuration period raise ValueError."""
    config = {
        "name": "Test Config",
        "description": "Test configuration",
        "start_date": "2025-05-01",
        "end_date": "2025-05-31",
        "employees": [
            {
                "id": 1,
                "name": "Test Employee",
                "max_days_in_a_row": 5,
                "off_days": ["2025-04-30"],  # Before start_date
                "max_hours_per_day": 8,
                "max_hours_in_period": 160,
                "work_percentage": 100
            }
        ],
        "duties": []
    }
    
    loader = ConfigLoader()
    with pytest.raises(ValueError, match="Invalid date format in off_days: 2025-04-30"):
        loader._validate_configuration(config)

def test_invalid_duty_fields():
    """Test that invalid duty fields raise ValueError."""
    config = {
        "name": "Test Config",
        "description": "Test configuration",
        "start_date": "2025-05-01",
        "end_date": "2025-05-31",
        "employees": [],
        "duties": [
            {
                "code": "TEST",
                # Missing required fields
                "start_time": "08:00"
            }
        ]
    }
    
    loader = ConfigLoader()
    with pytest.raises(ValueError, match="Duty must contain the key"):
        loader._validate_configuration(config)

def test_valid_duty_time_formats():
    """Test that both valid time formats are accepted."""
    config = {
        "name": "Test Config",
        "description": "Test configuration",
        "start_date": "2025-05-01",
        "end_date": "2025-05-31",
        "employees": [],
        "duties": [
            {
                "code": "TEST",
                "required_employees": 1,
                "start_time": "8:00",  # Without leading zero
                "end_time": "16:00"    # With leading zero
            }
        ]
    }
    
    loader = ConfigLoader()
    # Should not raise any exceptions
    loader._validate_configuration(config)
    
    # Test that the time format validation method works correctly
    assert loader._validate_time_format("8:00") == True
    assert loader._validate_time_format("08:00") == True
    assert loader._validate_time_format("8") == False
    assert loader._validate_time_format("8:0") == True  # This format is actually accepted
    assert loader._validate_time_format("8:") == False  # This format is not accepted

def test_invalid_duty_time_format():
    """Test that invalid duty time formats raise ValueError."""
    config = {
        "name": "Test Config",
        "description": "Test configuration",
        "start_date": "2025-05-01",
        "end_date": "2025-05-31",
        "employees": [],
        "duties": [
            {
                "code": "TEST",
                "required_employees": 1,
                "start_time": "8",  # Wrong format
                "end_time": "16:00"
            }
        ]
    }
    
    loader = ConfigLoader()
    with pytest.raises(ValueError, match="Invalid time format in duty"):
        loader._validate_configuration(config)

def test_invalid_duty_required_employees():
    """Test that invalid required_employees value raises ValueError."""
    config = {
        "name": "Test Config",
        "description": "Test configuration",
        "start_date": "2025-05-01",
        "end_date": "2025-05-31",
        "employees": [],
        "duties": [
            {
                "code": "TEST",
                "required_employees": 0,  # Invalid: must be positive
                "start_time": "08:00",
                "end_time": "16:00"
            }
        ]
    }
    
    loader = ConfigLoader()
    with pytest.raises(ValueError, match="required_employees must be a positive integer"):
        loader._validate_configuration(config)

def test_actual_configurations():
    """Test that all configuration files in the data directory are valid."""
    loader = ConfigLoader()
    config_files = loader.list_configurations()
    
    for config_name in config_files:
        config = loader.load_configuration(config_name)
        
        # Verify that the configuration has all required keys
        assert "name" in config
        assert "description" in config
        assert "start_date" in config
        assert "end_date" in config
        assert "employees" in config
        assert "duties" in config
        
        # Verify that the date formats are valid
        start_date = datetime.strptime(config["start_date"], "%Y-%m-%d")
        end_date = datetime.strptime(config["end_date"], "%Y-%m-%d")
        assert end_date >= start_date
        
        # Verify that each employee has all required fields
        for emp in config["employees"]:
            assert "id" in emp
            assert "name" in emp
            assert "max_days_in_a_row" in emp
            assert "off_days" in emp
            assert "max_hours_per_day" in emp
            assert "max_hours_in_period" in emp
            assert "work_percentage" in emp
            
            # Verify that numeric fields are valid
            assert isinstance(emp["max_days_in_a_row"], int) and emp["max_days_in_a_row"] >= 1
            assert isinstance(emp["max_hours_per_day"], int) and emp["max_hours_per_day"] >= 1
            assert isinstance(emp["max_hours_in_period"], int) and emp["max_hours_in_period"] >= 1
            assert isinstance(emp["work_percentage"], int) and 0 <= emp["work_percentage"] <= 100
            
            # Verify that off_days is a list
            assert isinstance(emp["off_days"], list)
            
            # Verify that each off_day is a valid date within the configuration period
            for off_day in emp["off_days"]:
                off_date = datetime.strptime(off_day, "%Y-%m-%d").date()
                assert start_date.date() <= off_date <= end_date.date()
        
        # Verify that each duty has all required fields
        for duty in config["duties"]:
            assert "code" in duty
            assert "required_employees" in duty
            assert "start_time" in duty
            assert "end_time" in duty
            
            # Verify that time formats are valid
            assert loader._validate_time_format(duty["start_time"])
            assert loader._validate_time_format(duty["end_time"])
            
            # Verify that required_employees is a positive integer
            assert isinstance(duty["required_employees"], int) and duty["required_employees"] >= 1

def test_overnight_duty_hours():
    """Test that overnight duty hours are calculated correctly."""
    config = {
        "name": "Test Config",
        "description": "Test configuration",
        "start_date": "2025-05-01",
        "end_date": "2025-05-01",
        "employees": [],
        "duties": [
            {
                "code": "NIGHT",
                "required_employees": 1,
                "start_time": "21:00",
                "end_time": "03:00"
            }
        ]
    }
    
    loader = ConfigLoader()
    expanded_duties = loader._expand_duties(config)
    
    # Should have 1 duty
    assert len(expanded_duties) == 1
    
    # Check duty
    assert expanded_duties[0]["date"] == "2025-05-01"
    assert expanded_duties[0]["id"] == 0
    assert expanded_duties[0]["code"] == "NIGHT"
    assert expanded_duties[0]["working_hours"] == 6.0  # 6 hours for overnight shift (21:00 to 03:00)

def test_late_night_duty_hours():
    """Test that late night duty hours are calculated correctly."""
    config = {
        "name": "Test Config",
        "description": "Test configuration",
        "start_date": "2025-05-01",
        "end_date": "2025-05-01",
        "employees": [],
        "duties": [
            {
                "code": "LATE",
                "required_employees": 1,
                "start_time": "23:00",
                "end_time": "01:00"
            }
        ]
    }
    
    loader = ConfigLoader()
    expanded_duties = loader._expand_duties(config)
    
    # Should have 1 duty
    assert len(expanded_duties) == 1
    
    # Check duty
    assert expanded_duties[0]["date"] == "2025-05-01"
    assert expanded_duties[0]["id"] == 0
    assert expanded_duties[0]["code"] == "LATE"
    assert expanded_duties[0]["working_hours"] == 2.0  # 2 hours for late night shift (23:00 to 01:00) 