import mysql.connector
import logging
import os
from contextlib import contextmanager
from typing import List, Dict, Optional

class ExpenseDatabase:
    """
    A class to handle all database operations for the expense manager.
    """

    def __init__(self, host=None, user=None, password=None, database=None):
        """
        Initializes the ExpenseDatabase object with database connection parameters.
        Credentials are loaded from environment variables if not provided.

        :param host: The database host (defaults to DB_HOST env var or 'localhost').
        :param user: The database user (defaults to DB_USER env var or 'root').
        :param password: The database user's password (defaults to DB_PASSWORD env var).
        :param database: The name of the database (defaults to DB_NAME env var or 'expense_manager').
        """
        self.host = host or os.getenv('DB_HOST', 'localhost')
        self.user = user or os.getenv('DB_USER', 'root')
        self.password = password or os.getenv('DB_PASSWORD', '1234')
        self.database = database or os.getenv('DB_NAME', 'expense_manager')
        logging.debug("ExpenseDatabase instance created.")

    @contextmanager
    def _get_db_cursor(self, commit=False):
        """
        A private context manager to handle database connections and cursors.
        It automatically handles the opening and closing of the database connection
        and cursor, and commits or rolls back the transaction as needed.

        :param commit: If True, commits the transaction upon exiting the context.
        """
        conn = None
        cursor = None
        try:
            conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            cursor = conn.cursor(dictionary=True)
            logging.debug("Database connection and cursor created.")
            yield cursor
            if commit and conn.is_connected():
                conn.commit()
                logging.debug("Database transaction committed.")
        except mysql.connector.Error as err:
            if commit and conn and conn.is_connected():
                conn.rollback()
                logging.warning(f"Database transaction rolled back due to error: {err}")
            logging.error(f"Database error: {err}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()
            logging.debug("Database connection and cursor closed.")

    def fetch_expenses_for_date(self, expense_date) -> List[Dict]:
        """
        Fetches all expenses for a specific date from the database.

        :param expense_date: The date for which to fetch expenses (YYYY-MM-DD format).
        :return: A list of dictionaries, where each dictionary represents an expense record.
        :raises mysql.connector.Error: If database operation fails.
        """
        logging.debug(f"Fetching expenses for date: {expense_date}")
        with self._get_db_cursor() as cursor:
            query = "SELECT * FROM expenses WHERE expense_date = %s"
            cursor.execute(query, (expense_date,))
            results = cursor.fetchall()
            logging.info(f"Found {len(results)} expenses for date: {expense_date}")
            return results

    def delete_expenses_for_date(self, expense_date) -> int:
        """
        Deletes all expenses for a specific date from the database.

        :param expense_date: The date for which to delete expenses (YYYY-MM-DD format).
        :return: Number of rows deleted.
        :raises mysql.connector.Error: If database operation fails.
        """
        logging.debug(f"Deleting expenses for date: {expense_date}")
        with self._get_db_cursor(commit=True) as cursor:
            query = "DELETE FROM expenses WHERE expense_date = %s"
            cursor.execute(query, (expense_date,))
            deleted_count = cursor.rowcount
            logging.info(f"Successfully deleted {deleted_count} expense(s) for date: {expense_date}")
            return deleted_count

    def insert_expense(self, expense_date, category, notes, amount) -> int:
        """
        Inserts a new expense record into the database.

        :param expense_date: The date of the expense (YYYY-MM-DD format).
        :param category: The category of the expense (e.g., 'Food', 'Transport').
        :param notes: Any notes related to the expense.
        :param amount: The amount of the expense.
        :return: The ID of the inserted expense record.
        :raises mysql.connector.Error: If database operation fails.
        """
        logging.debug(f"Inserting new expense: Date={expense_date}, Category={category}, Amount={amount}")
        with self._get_db_cursor(commit=True) as cursor:
            query = "INSERT INTO expenses (expense_date, category, notes, amount) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (expense_date, category, notes, amount))
            inserted_id = cursor.lastrowid
            logging.info(f"Successfully inserted new expense with ID: {inserted_id}")
            return inserted_id

    def fetch_expense_summary(self, start_date, end_date) -> List[Dict]:
        """
        Fetches a summary of expenses grouped by category within a given date range.

        :param start_date: The start date of the range (YYYY-MM-DD format).
        :param end_date: The end date of the range (YYYY-MM-DD format).
        :return: A list of dictionaries, each containing 'category' and 'total_amount'.
        :raises mysql.connector.Error: If database operation fails.
        """
        logging.debug(f"Fetching expense summary from {start_date} to {end_date}")
        with self._get_db_cursor() as cursor:
            query = """
                SELECT category, SUM(amount) as total_amount 
                FROM expenses 
                WHERE expense_date BETWEEN %s AND %s 
                GROUP BY category
            """
            cursor.execute(query, (start_date, end_date))
            results = cursor.fetchall()
            logging.info(f"Found expense summary for {len(results)} categories.")
            return results
