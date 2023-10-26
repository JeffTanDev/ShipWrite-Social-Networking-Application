import mysql.connector
from mysql.connector import pooling
from decouple import config

# Class that handles DB interactions


class DataBase:

    # Create pool of connections so they can be reused without having to open and close for each transaction
    def __init__(self) -> None:
        self.connection_pool = self._create_connection_pool()

    # Creates pool
    def _create_connection_pool(self):
        db_config = {"user": config('DB_USER'),
                     "password": config('DB_PASSWORD'),
                     "host": config('DB_HOST'),
                     "database": config('DB')}

        connection_pool = pooling.MySQLConnectionPool(
            pool_name="connection_pool", pool_size=5, pool_reset_session=True, **db_config)

        return connection_pool

    def insert_into_db(self, table_name: str, data: dict) -> bool:
        """
        Insert a new record into a specified database table with the provided data.

        Args:
            table_name (str): The name of the table in which to insert the data.
            data (dict): A dictionary containing the column names as keys and their corresponding
                values for the new record.

        Returns:
            bool: True if the insertion is successful, False otherwise.

        This function retrieves a database connection from the connection pool, constructs an
        INSERT SQL statement based on the provided table name and data, and executes the insertion.
        If successful, it commits the transaction and returns True. If an error occurs during
        the insertion process, it returns False and logs the error message.

        Example: insert_into_db("user_info", {'first_name': 'Jesse', 'last_name': 'Baxter' ... etc})

        """

        connection = self.connection_pool.get_connection()
        if connection is None:
            print("Database connection is not available.")
            return False

        insert = f"INSERT INTO {table_name} ({', '.join(data.keys())}) VALUES ({', '.join(['%s' for _ in data])})"
        values = tuple(data.values())

        try:
            with connection.cursor() as cursor:
                cursor.execute(insert, values)
                connection.commit()
            return True
        except mysql.connector.Error as e:
            print(f"Error: {e}")
            return False
        finally:
            connection.close()

    def select_from_db(self, table_name: str, data: dict) -> list:
        """
        Retrieve data from a specified database table using a SELECT query.

        Args:
            table_name (str): The name of the table from which to retrieve data.
            data (dict): A dictionary containing the following keys:
                - 'fields' (list): A list of column names to select.
                - 'formatting' (str, optional): Additional SQL formatting, such as WHERE clauses,
                JOIN statements, or ORDER BY clauses. If not provided, the query will select all records.

        Returns:
            list or None: A list of tuples representing the selected records. Returns None if an error occurs.

        This function retrieves a database connection from the connection pool, constructs a SELECT SQL statement
        based on the provided table name and data, and executes the query to retrieve the specified data.
        If successful, it returns the selected records as a list of tuples. If an error occurs during the selection process,
        it returns None and logs the error message.

        Example of a call: select_from_db("user_info", {"fields": ["first_name"], "formatting": None})

        Example of getting something out of the return value:
            names = DataBase.select_from_db(
            "user_info", {"fields": ["first_name"], "formatting": None})

            if names:
                for entry in names:
                    print(f"{entry[0]} is in the database!")

        """
        connection = self.connection_pool.get_connection()

        if connection is None:
            print("Database connection is not available.")
            return False

        select = f"SELECT {', '.join(data['fields'])} FROM {table_name} {data['formatting'] if data['formatting'] else ''}"

        try:
            with connection.cursor() as cursor:
                cursor.execute(select)
                result = cursor.fetchall()
            return result
        except mysql.connector.Error as e:
            print(f"Error: {e}")
            return None
        finally:
            connection.close()

    def update_values_in_db(self, table_name: str, data: dict, formatting: str) -> bool:
        """
        Update record in the database table with the provided data.

        Args:
            table_name (str): The name of the table to update records in.
            data (dict): A dictionary containing key-value pairs where the keys are column names
                        and the values are the new values to set in the specified table.
            formatting (str): Additional SQL formatting to be appended to the UPDATE statement.
                            For example, you can add conditions like WHERE clauses or LIMIT.

        Returns:
            bool: True if the update was successful, False otherwise.

        This method connects to the database using the connection pool, constructs an SQL UPDATE statement
        based on the provided data, and executes it. If the update is successful, it returns True; otherwise,
        it returns False.

        IMPORTANT:
            - There must be some kind of formatting passed in. You cannot edit a record without narrowing it down on some condition.
              If you do not pass a format string in the modification will change the value in the column for every single record.
        """

        connection = self.connection_pool.get_connection()

        if connection is None:
            print("Database connection is not available.")
            return False

        if formatting is None or formatting == '':
            return False

        update_formatted = ', '.join([f'{key}="{data[key]}"'for key in data])
        update = f"UPDATE {table_name} SET {update_formatted} {formatting}"

        try:
            with connection.cursor() as cursor:
                cursor.execute(update)
                connection.commit()
                return True
        except mysql.connector.Error as e:
            print(f"Error: {e}")
            return False
        finally:
            connection.close()
