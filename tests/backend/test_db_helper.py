import pytest
from unittest.mock import patch, MagicMock
import logging
from backend.db_helper import ExpenseDatabase
import mysql.connector

# Configure logging for tests
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@pytest.fixture
def db_helper():
    """
    Pytest fixture to create an instance of ExpenseDatabase
    for each test function.
    """
    logging.info("Creating ExpenseDatabase instance for a test.")
    return ExpenseDatabase()

def test_fetch_expenses_for_date_success(db_helper):
    """
    Test successful fetching of expenses for a specific date.
    It should call the database with the correct query and return the mocked data.
    """
    logging.info("Testing fetch_expenses_for_date: success case.")
    
    # Mock data to be returned by fetchall
    mock_expenses = [{'id': 1, 'expense_date': '2024-08-01', 'category': 'Rent', 'notes': 'Monthly rent', 'amount': 1227}]
    
    # Create a mock cursor
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = mock_expenses
    
    # Mock the context manager and the connection
    with patch('mysql.connector.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Call the method under test
        expenses = db_helper.fetch_expenses_for_date('2024-08-01')
        
        # Assertions
        mock_cursor.execute.assert_called_once_with("SELECT * FROM expenses WHERE expense_date = %s", ('2024-08-01',))
        assert expenses == mock_expenses
        assert len(expenses) > 0
        assert expenses[0]['amount'] == 1227
        assert expenses[0]['category'] == 'Rent'

def test_fetch_expenses_for_date_no_results(db_helper):
    """
    Test fetching expenses for a date with no results.
    It should return an empty list.
    """
    logging.info("Testing fetch_expenses_for_date: no results case.")
    
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = []
    
    with patch('mysql.connector.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        expenses = db_helper.fetch_expenses_for_date("9999-99-99")
        
        mock_cursor.execute.assert_called_once_with("SELECT * FROM expenses WHERE expense_date = %s", ("9999-99-99",))
        assert expenses == []
        assert len(expenses) == 0

def test_fetch_expenses_for_date_db_error(db_helper):
    """
    Test that fetch_expenses_for_date raises exception on database errors.
    """
    logging.info("Testing fetch_expenses_for_date: database error case.")
    
    with patch('mysql.connector.connect') as mock_connect:
        # Simulate a database connection error
        mock_connect.side_effect = mysql.connector.Error("Connection failed")
        
        # Expect the exception to be raised
        with pytest.raises(mysql.connector.Error):
            db_helper.fetch_expenses_for_date('2024-08-01')

def test_delete_expenses_for_date(db_helper):
    """
    Test successful deletion of expenses for a specific date.
    It should execute a DELETE query, commit the transaction, and return deleted count.
    """
    logging.info("Testing delete_expenses_for_date.")
    
    mock_cursor = MagicMock()
    mock_cursor.rowcount = 3  # Simulate 3 rows deleted
    
    with patch('mysql.connector.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        deleted_count = db_helper.delete_expenses_for_date('2024-08-01')
        
        mock_cursor.execute.assert_called_once_with("DELETE FROM expenses WHERE expense_date = %s", ('2024-08-01',))
        # Check that commit was called
        assert mock_conn.commit.called
        # Verify the return value
        assert deleted_count == 3

def test_insert_expense(db_helper):
    """
    Test successful insertion of a new expense.
    It should execute an INSERT query with correct parameters, commit, and return inserted ID.
    """
    logging.info("Testing insert_expense.")
    
    mock_cursor = MagicMock()
    mock_cursor.lastrowid = 42  # Simulate inserted ID
    
    with patch('mysql.connector.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        inserted_id = db_helper.insert_expense("2024-08-02", "Food", "Lunch", 25.50)
        
        expected_query = "INSERT INTO expenses (expense_date, category, notes, amount) VALUES (%s, %s, %s, %s)"
        expected_params = ("2024-08-02", "Food", "Lunch", 25.50)
        
        mock_cursor.execute.assert_called_once_with(expected_query, expected_params)
        assert mock_conn.commit.called
        # Verify the return value
        assert inserted_id == 42

def test_fetch_expense_summary(db_helper):
    """
    Test successful fetching of an expense summary.
    It should call the database with the correct query and return a summary.
    """
    logging.info("Testing fetch_expense_summary.")
    
    mock_summary = [{'category': 'Food', 'total_amount': 300.75}]
    
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = mock_summary
    
    with patch('mysql.connector.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        summary = db_helper.fetch_expense_summary("2024-08-01", "2024-08-31")
        
        expected_query = """
                    SELECT category, SUM(amount) as total_amount 
                    FROM expenses 
                    WHERE expense_date BETWEEN %s AND %s 
                    GROUP BY category
                """
        expected_params = ("2024-08-01", "2024-08-31")

        # We might need to be careful with whitespace in the query string
        mock_cursor.execute.assert_called_once()
        args, _ = mock_cursor.execute.call_args
        assert ' '.join(args[0].split()) == ' '.join(expected_query.split())
        assert args[1] == expected_params
        
        assert summary == mock_summary

def test_environment_variable_initialization():
    """
    Test that ExpenseDatabase loads configuration from environment variables.
    """
    logging.info("Testing environment variable initialization.")
    
    import os
    
    # Set environment variables
    with patch.dict(os.environ, {
        'DB_HOST': 'test-host',
        'DB_USER': 'test-user',
        'DB_PASSWORD': 'test-password',
        'DB_NAME': 'test-database'
    }):
        # Create a new instance
        test_db = ExpenseDatabase()
        
        # Verify that environment variables were loaded
        assert test_db.host == 'test-host'
        assert test_db.user == 'test-user'
        assert test_db.password == 'test-password'
        assert test_db.database == 'test-database'

def test_default_values_when_no_env_vars():
    """
    Test that ExpenseDatabase uses default values when no environment variables are set.
    """
    logging.info("Testing default values initialization.")
    
    import os
    
    # Ensure environment variables are not set
    env_vars = ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']
    original_values = {key: os.environ.get(key) for key in env_vars}
    
    try:
        # Remove environment variables
        for key in env_vars:
            os.environ.pop(key, None)
        
        # Create a new instance
        test_db = ExpenseDatabase()
        
        # Verify defaults are used
        assert test_db.host == 'localhost'
        assert test_db.user == 'root'
        assert test_db.password == '1234'
        assert test_db.database == 'expense_manager'
    finally:
        # Restore original environment
        for key, value in original_values.items():
            if value is not None:
                os.environ[key] = value

