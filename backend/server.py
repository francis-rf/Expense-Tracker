from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import date
from .db_helper import ExpenseDatabase
from pydantic import BaseModel, Field
from typing import List
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Centralized Logging Configuration ---

# Define the project root path (go up from backend to project root)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(PROJECT_ROOT, 'app.log')

# Ensure the log file path is accessible
print(f"Logging to: {LOG_FILE}")

# Configure logging to write to app.log in the project root directory
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, mode='a'),
        logging.StreamHandler()  # Also log to console
    ],
    force=True  # Force re-configuration of the root logger
)

# Get a logger for this module
logger = logging.getLogger(__name__)

# --- Database and App Initialization ---

try:
    db = ExpenseDatabase()
    logger.info("Successfully connected to the database.")
except Exception as e:
    logger.critical(f"Failed to connect to the database on startup: {e}")
    # The application will not be functional without a database connection.
    db = None 

app = FastAPI(
    title="Expense Manager API",
    description="API for managing personal expenses.",
    version="1.0.0",
)

# --- CORS Configuration ---
# Allow frontend applications to access this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---

class Expense(BaseModel):
    """Pydantic model for representing a single expense item."""
    category: str
    notes: str
    amount: float = Field(gt=0, description="Amount must be greater than 0")

class ExpenseSummary(BaseModel):
    """Pydantic model for representing a category-wise expense summary."""
    category: str
    total_amount: float

class ExpenseCreateResponse(BaseModel):
    """Response model for expense creation."""
    message: str
    inserted_count: int
    inserted_ids: List[int]

class ExpenseDeleteResponse(BaseModel):
    """Response model for expense deletion."""
    message: str
    deleted_count: int

# --- API Endpoints ---

@app.get('/')
def root():
    """
    Root endpoint providing API information.
    """
    return {
        "name": "Expense Manager API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "GET /": "API information",
            "GET /health": "Health check",
            "GET /expenses/{date}": "Get expenses for a date",
            "POST /expenses/{date}": "Add expenses for a date",
            "DELETE /expenses/{date}": "Delete expenses for a date",
            "GET /summary": "Get expense summary (requires start_date and end_date params)"
        }
    }

@app.get('/health')
def health_check():
    """
    Health check endpoint to verify API and database connectivity.
    """
    health_status = {
        "status": "healthy",
        "database": "disconnected"
    }
    
    if db:
        try:
            # Simple check to verify database connection
            db.fetch_expenses_for_date(date.today())
            health_status["database"] = "connected"
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            health_status["status"] = "degraded"
            health_status["database"] = "error"
    else:
        health_status["status"] = "unhealthy"
    
    return health_status

@app.get('/expenses/{expense_date}', response_model=List[Expense])
def get_expenses_for_date(expense_date: date):
    """
    Fetches all expenses recorded for a specific date.
    """
    logger.info(f"Request received: GET /expenses/{expense_date}")
    if not db:
        raise HTTPException(status_code=503, detail="Database connection is not available.")
    try:
        expenses_for_date = db.fetch_expenses_for_date(expense_date)
        logger.info(f"Successfully fetched {len(expenses_for_date)} expenses for {expense_date}.")
        return expenses_for_date
    except Exception as e:
        logger.error(f"Error fetching expenses for date {expense_date}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal server error occurred while fetching expenses.")

@app.post('/expenses/{expense_date}', response_model=ExpenseCreateResponse)
def add_expenses_for_date(expense_date: date, expenses: List[Expense]):
    """
    Adds one or more new expense records for a specific date.
    Returns the IDs of the inserted records.
    """
    logger.info(f"Request received: POST /expenses/{expense_date} with {len(expenses)} items.")
    if not db:
        raise HTTPException(status_code=503, detail="Database connection is not available.")
    try:
        inserted_ids = []
        for expense in expenses:
            expense_id = db.insert_expense(expense_date, expense.category, expense.notes, expense.amount)
            inserted_ids.append(expense_id)
        logger.info(f"Successfully inserted {len(expenses)} new expenses for date: {expense_date}")
        return ExpenseCreateResponse(
            message=f"Successfully added {len(expenses)} expense(s) for {expense_date}.",
            inserted_count=len(inserted_ids),
            inserted_ids=inserted_ids
        )
    except Exception as e:
        logger.error(f"Error inserting expenses for date {expense_date}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal server error occurred while adding expenses.")

@app.delete('/expenses/{expense_date}', response_model=ExpenseDeleteResponse)
def delete_expenses_for_date(expense_date: date):
    """
    Deletes all expenses associated with a specific date.
    Returns the count of deleted records.
    """
    logger.info(f"Request received: DELETE /expenses/{expense_date}")
    if not db:
        raise HTTPException(status_code=503, detail="Database connection is not available.")
    try:
        deleted_count = db.delete_expenses_for_date(expense_date)
        logger.info(f"Successfully deleted {deleted_count} expense(s) for date: {expense_date}")
        return ExpenseDeleteResponse(
            message=f"Successfully deleted {deleted_count} expense(s) for {expense_date}.",
            deleted_count=deleted_count
        )
    except Exception as e:
        logger.error(f"Error deleting expenses for date {expense_date}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal server error occurred while deleting expenses.")

@app.get('/summary', response_model=List[ExpenseSummary])
def get_expense_summary(start_date: date, end_date: date):
    """
    Fetches a summary of expenses grouped by category over a specified date range.
    """
    logger.info(f"Request received: GET /summary?start_date={start_date}&end_date={end_date}")
    if not db:
        raise HTTPException(status_code=503, detail="Database connection is not available.")
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="The start_date cannot be after the end_date.")
    try:
        summary = db.fetch_expense_summary(start_date, end_date)
        logger.info(f"Successfully fetched summary for {len(summary)} categories between {start_date} and {end_date}.")
        return summary
    except Exception as e:
        logger.error(f"Error fetching expense summary from {start_date} to {end_date}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal server error occurred while fetching the summary.")
