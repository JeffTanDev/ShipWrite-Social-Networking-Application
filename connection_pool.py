from mysql.connector import pooling
from decouple import config

class ConnectionPool:
    @staticmethod
    def create_pool(pool_size_passed=5):
        db_config = {
            "user": config('DB_USER'),
            "password": config('DB_PASSWORD'),
            "host": config('DB_HOST'),
            "database": config('DB')
        }

        connection_pool = pooling.MySQLConnectionPool(
            pool_name="connection_pool", pool_size=pool_size_passed, pool_reset_session=True, **db_config)

        return connection_pool
