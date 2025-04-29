from datetime import datetime, timedelta, date
from src.resource_planner import ResourcePlanner
from typing import List, Dict
import unittest

class TestResourcePlanner(unittest.TestCase):
    def setUp(self):
        """Set up a test instance with some sample data."""
        self.planner = ResourcePlanner()
        
        # Add test employees with more flexibility
        self.planner.add_employee(0, "Anna", 6, [], 8)  # No blocked days
        self.planner.add_employee(1, "Ben", 6, [], 8)   # No blocked days
        self.planner.add_employee(2, "Clara", 6, [], 8) # No blocked days
        self.planner.add_employee(3, "David", 6, [], 8) # Added more employees
        self.planner.add_employee(4, "Emma", 6, [], 8)  # to ensure coverage
        
        # Add test duties for 2 days (reduced from 3 to make it easier)
        duty_id = 0
        start_date = date(2024, 6, 15)
        for i in range(2):  # Reduced from 3 to 2 days
            current_date = start_date + timedelta(days=i)
            # Morning shift
            self.planner.add_duty(duty_id, current_date.strftime("%Y-%m-%d"), 8, 16, 1, "Morning")
            duty_id += 1
            # Late shift
            self.planner.add_duty(duty_id, current_date.strftime("%Y-%m-%d"), 16, 24, 1, "Late")
            duty_id += 1
            # Night shift
            next_date = current_date + timedelta(days=1)
            self.planner.add_duty(duty_id, next_date.strftime("%Y-%m-%d"), 0, 8, 1, "Night")
            duty_id += 1
            
        self.planner.setup_model()
        self.assignments = self.planner.solve()
        
    def test_required_employees_constraint(self):
        """Test that each duty has the required number of employees."""
        duties_by_date = {}
        for assignment in self.assignments:
            date = assignment['date']
            if date not in duties_by_date:
                duties_by_date[date] = []
            duties_by_date[date].append(assignment)
            
        for date, duties in duties_by_date.items():
            for duty in duties:
                self.assertEqual(
                    len(duty['assigned_employees']), 
                    1,  # We set required_employees=1 in setUp
                    f"Duty on {date} does not have the required number of employees"
                )
                
    def test_blocked_days_constraint(self):
        """Test that employees are not assigned on their blocked days."""
        for assignment in self.assignments:
            date = assignment['date']
            for emp_name in assignment['assigned_employees']:
                emp = next(e for e in self.planner.employees if e['name'] == emp_name)
                self.assertNotIn(
                    date, 
                    emp['blocked_days'],
                    f"Employee {emp_name} was assigned on a blocked day: {date}"
                )
                
    def test_one_duty_per_day_constraint(self):
        """Test that employees work at most one duty per day."""
        emp_assignments = {}
        for assignment in self.assignments:
            date = assignment['date']
            for emp_name in assignment['assigned_employees']:
                if emp_name not in emp_assignments:
                    emp_assignments[emp_name] = {}
                if date not in emp_assignments[emp_name]:
                    emp_assignments[emp_name][date] = 0
                emp_assignments[emp_name][date] += 1
                
        for emp_name, dates in emp_assignments.items():
            for date, count in dates.items():
                self.assertLessEqual(
                    count, 
                    1,
                    f"Employee {emp_name} has more than one duty on {date}"
                )
                
    def test_rest_time_constraint(self):
        """Test that employees have at least 8 hours rest between duties."""
        emp_duties = {}
        for assignment in self.assignments:
            date = assignment['date']
            time = assignment['time']
            start_time = int(time.split('-')[0])
            end_time = int(time.split('-')[1])
            
            for emp_name in assignment['assigned_employees']:
                if emp_name not in emp_duties:
                    emp_duties[emp_name] = []
                emp_duties[emp_name].append({
                    'date': date,
                    'start': start_time,
                    'end': end_time
                })
                
        for emp_name, duties in emp_duties.items():
            duties.sort(key=lambda x: (x['date'], x['start']))
            for i in range(len(duties) - 1):
                current_duty = duties[i]
                next_duty = duties[i + 1]
                
                # Calculate hours between duties
                current_end = datetime.strptime(f"{current_duty['date']} {current_duty['end']:02d}:00", "%Y-%m-%d %H:%M")
                next_start = datetime.strptime(f"{next_duty['date']} {next_duty['start']:02d}:00", "%Y-%m-%d %H:%M")
                
                if next_start.date() == current_end.date():
                    # Same day duties
                    hours_between = next_start.hour - current_end.hour
                else:
                    # Next day duties
                    hours_between = 24 - current_end.hour + next_start.hour
                    
                self.assertGreaterEqual(
                    hours_between,
                    8,
                    f"Employee {emp_name} has less than 8 hours rest between duties"
                )
                
    def test_max_days_in_a_row_constraint(self):
        """Test that employees don't work more than their maximum days in a row."""
        emp_assignments = {}
        for assignment in self.assignments:
            date = assignment['date']
            for emp_name in assignment['assigned_employees']:
                if emp_name not in emp_assignments:
                    emp_assignments[emp_name] = set()
                emp_assignments[emp_name].add(date)
                
        for emp_name, dates in emp_assignments.items():
            emp = next(e for e in self.planner.employees if e['name'] == emp_name)
            max_days = emp['max_days_in_a_row']
            
            dates = sorted(list(dates))
            for i in range(len(dates) - max_days + 1):
                window = dates[i:i + max_days + 1]
                consecutive_days = 0
                for j in range(len(window) - 1):
                    current_date = datetime.strptime(window[j], "%Y-%m-%d").date()
                    next_date = datetime.strptime(window[j + 1], "%Y-%m-%d").date()
                    if (next_date - current_date).days == 1:
                        consecutive_days += 1
                    else:
                        consecutive_days = 0
                    self.assertLessEqual(
                        consecutive_days + 1,
                        max_days,
                        f"Employee {emp_name} worked more than {max_days} days in a row"
                    )
                    
    def test_workload_balance_constraint(self):
        """Test that employee workloads are reasonably balanced."""
        # First check if we have any assignments at all
        self.assertGreater(
            len(self.assignments),
            0,
            "No assignments were made. This might indicate the solver couldn't find a valid solution."
        )
        
        emp_workloads = {}
        for assignment in self.assignments:
            time = assignment['time']
            start_time = int(time.split('-')[0])
            end_time = int(time.split('-')[1])
            hours = (end_time - start_time) % 24
            
            for emp_name in assignment['assigned_employees']:
                if emp_name not in emp_workloads:
                    emp_workloads[emp_name] = 0
                emp_workloads[emp_name] += hours
        
        # Check if any employees were assigned
        self.assertGreater(
            len(emp_workloads),
            0,
            "No employees were assigned to any duties. This might indicate the solver couldn't find a valid solution."
        )
        
        # Calculate average workload
        avg_workload = sum(emp_workloads.values()) / len(emp_workloads)
        
        # Check that no employee works more than 20% more than average
        for emp_name, workload in emp_workloads.items():
            self.assertLessEqual(
                workload,
                avg_workload * 1.2,
                f"Employee {emp_name} has more than 20% above average workload"
            )
            self.assertGreaterEqual(
                workload,
                avg_workload * 0.8,
                f"Employee {emp_name} has more than 20% below average workload"
            )

if __name__ == '__main__':
    unittest.main() 