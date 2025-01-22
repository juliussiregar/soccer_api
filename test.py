from app.core.database import get_session
from app.core.config import settings
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql import text
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def test_database_connection():
    """Test the database connection."""
    try:
        logging.info("Testing database connection...")
        with get_session() as session:
            # Use SQLAlchemy's `text` for the query
            result = session.execute(text("SELECT 1")).scalar()
            if result == 1:
                logging.info("Database connection successful!")
            else:
                logging.error("Unexpected result from test query.")
    except OperationalError as e:
        logging.error("Database connection failed. Please check your settings.")
        logging.error(f"Error: {e}")
    except Exception as e:
        logging.error("An unexpected error occurred while testing the database connection.")
        logging.error(f"Error: {e}")

if __name__ == "__main__":
    logging.info("Database URI: %s", settings.database_uri)
    test_database_connection()
