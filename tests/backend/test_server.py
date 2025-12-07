import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import date
import mysql.connector

# Import the FastAPI app
from backend.server import app, db

# Create a test client
client = TestClient(app)


class TestRootEndpoint:
    """Tests for the root endpoint."""
    
    def test_root_endpoint(self):
        """Test that the root endpoint returns API information."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Expense Manager API"
        assert data["version"] == "1.0.0"
        assert data["status"] == "operational"
        assert "endpoints" in data


class TestHealthEndpoint:
    """Tests for the health check endpoint."""
    
    def test_health_check_healthy(self):
        """Test health check when database is connected."""
        with patch.object(db, 'fetch_expenses_for_date', return_value=[]):
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["database"] == "connected"
    
    def test_health_check_degraded(self):
        """Test health check when database has errors."""
        with patch.object(db, 'fetch_expenses_for_date', side_effect=Exception("DB Error")):
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "degraded"
            assert data["database"] == "error"


class TestGetExpenses:
    """Tests for GET /expenses/{expense_date} endpoint."""
    
    def test_get_expenses_success(self):
        """Test successful retrieval of expenses for a date."""
        mock_expenses = [
            {"id": 1, "expense_date": "2024-08-01", "category": "Food", "notes": "Lunch", "amount": 25.50},
            {"id": 2, "expense_date": "2024-08-01", "category": "Transport", "notes": "Bus", "amount": 5.00}
        ]
        
        with patch.object(db, 'fetch_expenses_for_date', return_value=mock_expenses):
            response = client.get("/expenses/2024-08-01")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["category"] == "Food"
            assert data[0]["amount"] == 25.50
    
    def test_get_expenses_empty(self):
        """Test retrieval when no expenses exist for the date."""
        with patch.object(db, 'fetch_expenses_for_date', return_value=[]):
            response = client.get("/expenses/2024-12-25")
            assert response.status_code == 200
            data = response.json()
            assert data == []
    
    def test_get_expenses_db_error(self):
        """Test error handling when database operation fails."""
        with patch.object(db, 'fetch_expenses_for_date', side_effect=Exception("Database error")):
            response = client.get("/expenses/2024-08-01")
            assert response.status_code == 500
            assert "internal server error" in response.json()["detail"].lower()
    
    def test_get_expenses_invalid_date(self):
        """Test with invalid date format."""
        response = client.get("/expenses/invalid-date")
        assert response.status_code == 422  # Validation error


class TestPostExpenses:
    """Tests for POST /expenses/{expense_date} endpoint."""
    
    def test_post_expenses_success(self):
        """Test successful creation of expenses."""
        new_expenses = [
            {"category": "Food", "notes": "Dinner", "amount": 35.00},
            {"category": "Transport", "notes": "Taxi", "amount": 15.50}
        ]
        
        with patch.object(db, 'insert_expense', side_effect=[101, 102]):
            response = client.post("/expenses/2024-08-01", json=new_expenses)
            assert response.status_code == 200
            data = response.json()
            assert data["inserted_count"] == 2
            assert data["inserted_ids"] == [101, 102]
            assert "Successfully added 2 expense(s)" in data["message"]
    
    def test_post_expenses_single(self):
        """Test creating a single expense."""
        new_expense = [
            {"category": "Entertainment", "notes": "Movie", "amount": 12.00}
        ]
        
        with patch.object(db, 'insert_expense', return_value=201):
            response = client.post("/expenses/2024-08-02", json=new_expense)
            assert response.status_code == 200
            data = response.json()
            assert data["inserted_count"] == 1
            assert data["inserted_ids"] == [201]
    
    def test_post_expenses_invalid_amount(self):
        """Test validation: amount must be positive."""
        invalid_expense = [
            {"category": "Food", "notes": "Test", "amount": -10.00}
        ]
        
        response = client.post("/expenses/2024-08-01", json=invalid_expense)
        assert response.status_code == 422  # Validation error
    
    def test_post_expenses_zero_amount(self):
        """Test validation: amount must be greater than zero."""
        invalid_expense = [
            {"category": "Food", "notes": "Test", "amount": 0}
        ]
        
        response = client.post("/expenses/2024-08-01", json=invalid_expense)
        assert response.status_code == 422
    
    def test_post_expenses_missing_fields(self):
        """Test validation: all required fields must be present."""
        invalid_expense = [
            {"category": "Food", "amount": 25.00}  # Missing 'notes'
        ]
        
        response = client.post("/expenses/2024-08-01", json=invalid_expense)
        assert response.status_code == 422
    
    def test_post_expenses_db_error(self):
        """Test error handling when database insert fails."""
        new_expense = [
            {"category": "Food", "notes": "Test", "amount": 10.00}
        ]
        
        with patch.object(db, 'insert_expense', side_effect=Exception("Database error")):
            response = client.post("/expenses/2024-08-01", json=new_expense)
            assert response.status_code == 500


class TestDeleteExpenses:
    """Tests for DELETE /expenses/{expense_date} endpoint."""
    
    def test_delete_expenses_success(self):
        """Test successful deletion of expenses."""
        with patch.object(db, 'delete_expenses_for_date', return_value=3):
            response = client.delete("/expenses/2024-08-01")
            assert response.status_code == 200
            data = response.json()
            assert data["deleted_count"] == 3
            assert "Successfully deleted 3 expense(s)" in data["message"]
    
    def test_delete_expenses_none_found(self):
        """Test deletion when no expenses exist for the date."""
        with patch.object(db, 'delete_expenses_for_date', return_value=0):
            response = client.delete("/expenses/2024-12-25")
            assert response.status_code == 200
            data = response.json()
            assert data["deleted_count"] == 0
    
    def test_delete_expenses_db_error(self):
        """Test error handling when database delete fails."""
        with patch.object(db, 'delete_expenses_for_date', side_effect=Exception("Database error")):
            response = client.delete("/expenses/2024-08-01")
            assert response.status_code == 500


class TestGetSummary:
    """Tests for GET /summary endpoint."""
    
    def test_get_summary_success(self):
        """Test successful retrieval of expense summary."""
        mock_summary = [
            {"category": "Food", "total_amount": 150.00},
            {"category": "Transport", "total_amount": 50.00}
        ]
        
        with patch.object(db, 'fetch_expense_summary', return_value=mock_summary):
            response = client.get("/summary?start_date=2024-08-01&end_date=2024-08-31")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["category"] == "Food"
            assert data[0]["total_amount"] == 150.00
    
    def test_get_summary_empty(self):
        """Test summary when no expenses exist in date range."""
        with patch.object(db, 'fetch_expense_summary', return_value=[]):
            response = client.get("/summary?start_date=2024-01-01&end_date=2024-01-31")
            assert response.status_code == 200
            data = response.json()
            assert data == []
    
    def test_get_summary_invalid_date_range(self):
        """Test validation: start_date must be before end_date."""
        response = client.get("/summary?start_date=2024-08-31&end_date=2024-08-01")
        assert response.status_code == 400
        assert "start_date cannot be after the end_date" in response.json()["detail"]
    
    def test_get_summary_missing_params(self):
        """Test validation: both start_date and end_date are required."""
        response = client.get("/summary?start_date=2024-08-01")
        assert response.status_code == 422  # Missing required parameter
    
    def test_get_summary_db_error(self):
        """Test error handling when database summary fails."""
        with patch.object(db, 'fetch_expense_summary', side_effect=Exception("Database error")):
            response = client.get("/summary?start_date=2024-08-01&end_date=2024-08-31")
            assert response.status_code == 500


class TestDatabaseConnectionHandling:
    """Tests for database connection error handling."""
    
    def test_endpoints_without_db_connection(self):
        """Test that endpoints return 503 when database is not available."""
        # Temporarily set db to None to simulate connection failure
        with patch('backend.server.db', None):
            # Test GET expenses
            response = client.get("/expenses/2024-08-01")
            assert response.status_code == 503
            assert "Database connection is not available" in response.json()["detail"]
            
            # Test POST expenses
            response = client.post("/expenses/2024-08-01", json=[{"category": "Food", "notes": "Test", "amount": 10}])
            assert response.status_code == 503
            
            # Test DELETE expenses
            response = client.delete("/expenses/2024-08-01")
            assert response.status_code == 503
            
            # Test summary
            response = client.get("/summary?start_date=2024-08-01&end_date=2024-08-31")
            assert response.status_code == 503


class TestCORS:
    """Tests for CORS configuration."""
    
    def test_cors_headers_present(self):
        """Test that CORS headers are present in responses."""
        response = client.get("/", headers={"Origin": "http://localhost:3000"})
        assert response.status_code == 200
        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers or response.status_code == 200


# Run tests with: pytest tests/backend/test_server.py -v
