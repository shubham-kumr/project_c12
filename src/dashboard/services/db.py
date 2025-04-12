"""
SQLite database service for Project-C12.
Handles persistent storage of CO2 savings and query optimization metrics.
"""

import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseService:
    """Service for managing SQLite database operations."""
    
    def __init__(self, db_path: str = "data/metrics.db"):
        """
        Initialize database service.
        
        Args:
            db_path: Path to SQLite database file
        """
        # Ensure data directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.db_path = db_path
        self._initialize_db()
    
    def _initialize_db(self):
        """Create necessary tables if they don't exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create metrics table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        co2_saved REAL NOT NULL DEFAULT 0,
                        queries_optimized INTEGER NOT NULL DEFAULT 0,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Insert initial record if none exists
                cursor.execute("SELECT COUNT(*) FROM metrics")
                if cursor.fetchone()[0] == 0:
                    cursor.execute("""
                        INSERT INTO metrics (co2_saved, queries_optimized)
                        VALUES (0, 0)
                    """)
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except sqlite3.Error as e:
            logger.error(f"Database initialization failed: {str(e)}")
            raise
    
    def get_metrics(self) -> Dict[str, float]:
        """
        Get current CO2 savings metrics.
        
        Returns:
            Dictionary containing co2_saved and queries_optimized
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT co2_saved, queries_optimized, last_updated
                    FROM metrics
                    ORDER BY id DESC
                    LIMIT 1
                """)
                row = cursor.fetchone()
                return {
                    "co2_saved": float(row[0]),
                    "queries_optimized": int(row[1]),
                    "last_updated": row[2]
                }
        except sqlite3.Error as e:
            logger.error(f"Failed to get metrics: {str(e)}")
            return {"co2_saved": 0.0, "queries_optimized": 0}
    
    def update_metrics(self, co2_saved: float, queries_optimized: int) -> bool:
        """
        Update CO2 savings metrics.
        
        Args:
            co2_saved: Total CO2 saved in grams
            queries_optimized: Number of optimized queries
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE metrics
                    SET co2_saved = ?, 
                        queries_optimized = ?,
                        last_updated = CURRENT_TIMESTAMP
                    WHERE id = (SELECT id FROM metrics ORDER BY id DESC LIMIT 1)
                """, (co2_saved, queries_optimized))
                conn.commit()
                logger.info(f"Updated metrics: CO2 saved={co2_saved}g, Queries optimized={queries_optimized}")
                return True
        except sqlite3.Error as e:
            logger.error(f"Failed to update metrics: {str(e)}")
            return False
    
    def add_savings(self, co2_saved: float, query_optimized: bool = True) -> bool:
        """
        Add new CO2 savings to the total.
        
        Args:
            co2_saved: Additional CO2 saved in grams
            query_optimized: Whether this saving came from an optimized query
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get current metrics
                cursor.execute("""
                    SELECT co2_saved, queries_optimized
                    FROM metrics
                    ORDER BY id DESC
                    LIMIT 1
                """)
                current = cursor.fetchone()
                
                # Calculate new values
                new_co2 = float(current[0]) + co2_saved
                new_queries = int(current[1]) + (1 if query_optimized else 0)
                
                # Update metrics
                cursor.execute("""
                    UPDATE metrics
                    SET co2_saved = ?,
                        queries_optimized = ?,
                        last_updated = CURRENT_TIMESTAMP
                    WHERE id = (SELECT id FROM metrics ORDER BY id DESC LIMIT 1)
                """, (new_co2, new_queries))
                
                conn.commit()
                logger.info(f"Added CO2 savings: +{co2_saved}g, Total={new_co2}g")
                return True
        except sqlite3.Error as e:
            logger.error(f"Failed to add savings: {str(e)}")
            return False
