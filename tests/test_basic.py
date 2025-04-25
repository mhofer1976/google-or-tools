def test_imports():
    """Test that OR-Tools can be imported correctly."""
    from ortools.linear_solver import pywraplp
    assert pywraplp is not None
