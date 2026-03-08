"""
Database connection pooling for Smart Pet Feeder.

Provides MySQL connection pool management for improved performance and resource management.
"""

import logging

from mysql.connector import Error, pooling

logger = logging.getLogger(__name__)


class DatabasePool:
    """Singleton database connection pool manager."""

    _instance = None
    _pool = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabasePool, cls).__new__(cls)
        return cls._instance

    def initialize(self, config):
        """
        Initialize the connection pool.

        Args:
            config: Dict with database configuration (host, user, password, database)
        """
        if self._pool is not None:
            logger.warning("Connection pool already initialized")
            return

        try:
            self._pool = pooling.MySQLConnectionPool(
                pool_name="petfeeder_pool",
                pool_size=10,
                pool_reset_session=True,
                host=config.get("MYSQL_HOST"),
                user=config.get("MYSQL_USER"),
                password=config.get("MYSQL_PASSWORD"),
                database=config.get("MYSQL_DB"),
                port=config.get("MYSQL_PORT", 3306),
            )
            logger.info("[OK] Database pool initialized (size: 10)")
        except Error as err:
            logger.error(f"Failed to create connection pool: {err}")
            raise

    def get_connection(self):
        """
        Get a connection from the pool.

        Returns:
            mysql.connector.pooling.PooledMySQLConnection: Database connection

        Raises:
            Error: If pool not initialized or connection unavailable
        """
        if self._pool is None:
            raise Error("Connection pool not initialized. Call initialize() first.")

        try:
            connection = self._pool.get_connection()
            return connection
        except Error as err:
            logger.error(f"Failed to get connection from pool: {err}")
            raise

    def close_pool(self):
        """Close all connections in the pool."""
        if self._pool:
            # Connection pool doesn't have explicit close method
            # Connections are closed when app shuts down
            logger.info("Connection pool cleanup initiated")
            self._pool = None


# Global database pool instance
db_pool = DatabasePool()
