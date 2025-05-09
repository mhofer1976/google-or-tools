from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from ortools.sat.python import cp_model


class BaseConstraint(ABC):
    """
    Base class for all constraints in the resource planning system.

    Each constraint must implement:
    1. apply() - Adds the constraint to the solver model
    2. validate() - Validates that a solution satisfies the constraint
    """

    def __init__(
        self,
        model: cp_model.CpModel,
        assignments: Dict,
        employees: List[Dict],
        duties: List[Dict],
    ):
        """
        Initialize the constraint with the solver model and data.

        Args:
            model: The CP-SAT model to add constraints to
            assignments: Dictionary mapping (employee_id, duty_id) to solver variables
            employees: List of employee dictionaries
            duties: List of duty dictionaries
        """
        self.model = model
        self.assignments = assignments
        self.employees = employees
        self.duties = duties

    @abstractmethod
    def apply(self) -> None:
        """
        Apply this constraint to the solver model.

        This method should add all necessary constraints to the model.
        """
        pass

    @abstractmethod
    def validate(self, assignments: List[Dict[str, Any]]) -> bool:
        """
        Validate that assignments satisfy this constraint.
        
        Args:
            assignments: List of assignment dictionaries from the solver
            
        Returns:
            True if the assignments satisfy the constraint, False otherwise
        """
        pass

    def get_employee_assignments(
        self, assignments: List[Dict[str, Any]], employee_id: int
    ) -> List[Dict[str, Any]]:
        """
        Helper method to get all assignments for a specific employee.

        Args:
            assignments: List of assignment dictionaries from the solver
            employee_id: ID of the employee

        Returns:
            List of assignments for this employee
        """
        if not any(emp["id"] == employee_id for emp in self.employees):
            return []

        # Return all assignments for this employee
        return [
            assignment for assignment in assignments
            if isinstance(assignment, dict) and "employees" in assignment
            and any(emp["employee_id"] == employee_id for emp in assignment["employees"])
        ]

    def get_duty_by_id(self, duty_id: int) -> Optional[Dict[str, Any]]:
        """
        Helper method to get a duty by its ID.

        Args:
            duty_id: ID of the duty

        Returns:
            Duty dictionary or None if not found
        """
        return next((duty for duty in self.duties if duty["id"] == duty_id), None)

    def get_employee_by_id(self, employee_id: int) -> Optional[Dict[str, Any]]:
        """
        Helper method to get an employee by their ID.

        Args:
            employee_id: ID of the employee

        Returns:
            Employee dictionary or None if not found
        """
        return next((emp for emp in self.employees if emp["id"] == employee_id), None)
