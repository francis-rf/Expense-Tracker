# Testing Guide

## Setup

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Ensure you're in the project root directory:**
   ```bash
   cd c:\Users\franc\Desktop\Python Projects\Expenses_project
   ```

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test Files

```bash
# Test db_helper only
pytest tests/backend/test_db_helper.py

# Test server only
pytest tests/backend/test_server.py
```

### Run with Verbose Output

```bash
pytest -v
```

### Run with Coverage Report

```bash
pytest --cov=backend --cov-report=html
```

This will generate an HTML coverage report in `htmlcov/index.html`

### Run Specific Test Classes or Functions

```bash
# Run a specific test class
pytest tests/backend/test_server.py::TestGetExpenses

# Run a specific test function
pytest tests/backend/test_server.py::TestGetExpenses::test_get_expenses_success
```

### Run Tests Matching a Pattern

```bash
# Run all tests with "error" in the name
pytest -k error

# Run all tests with "validation" in the name
pytest -k validation
```

## Test Coverage

Current test coverage includes:

### `test_db_helper.py` (11 tests)

- ✅ `fetch_expenses_for_date` - success, no results, database errors
- ✅ `delete_expenses_for_date` - success with return value verification
- ✅ `insert_expense` - success with inserted ID verification
- ✅ `fetch_expense_summary` - success
- ✅ Environment variable loading
- ✅ Default value fallback

### `test_server.py` (30+ tests)

- ✅ Root endpoint (`/`)
- ✅ Health check endpoint (`/health`)
- ✅ GET expenses - success, empty, errors, invalid dates
- ✅ POST expenses - success, validation (negative amounts, zero, missing fields)
- ✅ DELETE expenses - success, none found, errors
- ✅ GET summary - success, empty, invalid date range, missing params
- ✅ Database connection error handling (503 responses)
- ✅ CORS configuration

## Test Structure

```
tests/
├── __init__.py
├── backend/
│   ├── __init__.py
│   ├── test_db_helper.py    # Database layer tests
│   └── test_server.py        # API endpoint tests
└── frontend/
    └── (frontend tests if applicable)
```

## Writing New Tests

### Template for db_helper tests:

```python
def test_new_feature(db_helper):
    """Description of what is being tested."""
    with patch('mysql.connector.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Your test code here
        result = db_helper.your_method()

        # Assertions
        assert result == expected_value
```

### Template for server tests:

```python
def test_new_endpoint():
    """Description of what is being tested."""
    with patch.object(db, 'method_name', return_value=mock_data):
        response = client.get("/your-endpoint")
        assert response.status_code == 200
        assert response.json() == expected_data
```

## Continuous Integration

To run tests in CI/CD:

```bash
pytest --cov=backend --cov-report=xml --cov-report=term
```

## Troubleshooting

### Import Errors

Make sure you're running from the project root and the backend package is accessible:

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Database Connection in Tests

All database operations are mocked in tests - no actual database connection is needed.

### Test Isolation

Each test is independent. Fixtures ensure clean state for each test.
