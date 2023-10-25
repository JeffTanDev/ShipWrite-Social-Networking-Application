import mysql.connector
import uuid
import bcrypt
import datetime


class UserManager():
    """
    A class responsible for user management and authentication.

    Args:
        database: An instance of the database connection manager (DataBase) for interacting with the database.

    Attributes:
        database: The database connection manager used for user-related database operations.
    """

    def __init__(self, database) -> None:
        """
        Initialize a new UserManager instance.

        Args:
            database: An instance of the database connection manager (DB).
        """

        self.database = database

    def hash_password(self, password: str) -> str:
        """
        Hash a given password using bcrypt.

        Args:
            password (str): The plaintext password to be hashed.

        Returns:
            tuple: A tuple containing the hashed password and salt used in the hashing process.
        """

        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return (hashed_password, salt)

    def check_password(self, password: str, username: str) -> bool:
        """
        Check if a provided password matches the stored password for a given username.

        Args:
            password (str): The plaintext password to be checked.
            username (str): The username associated with the stored password.

        Returns:
            bool: True if the password is correct; False otherwise.
        """

        stored_info = self.database.select_from_db('user_info', {'fields': [
            'password', 'password_salt'], 'formatting': f'WHERE username = "{username}"'})

        rehashed_password = bcrypt.hashpw(
            password.encode('utf-8'), stored_info[0][1].encode('utf-8'))

        return rehashed_password.decode("utf-8") == stored_info[0][0]

    def check_username(self, username: str) -> bool:
        """
        Check if a username exists in the user database.

        Args:
            username (str): The username to be checked for existence.

        Returns:
            bool: True if the username exists in the database; False otherwise.
        """

        query_result = self.database.select_from_db('user_info', {'fields': [
            'username'], 'formatting': f'WHERE username = "{username}"'})
        return True if query_result else False

    def create_user(self, data: dict) -> bool:
        """
        Create a new user in the user database.

        Args:
            data (dict): A dictionary containing user data, including username and password.

        Returns:
            bool: True if the user was successfully created; False if an error occurred.
        """

        hash_result = self.hash_password(data['password'])
        data['password'] = hash_result[0]
        data['password_salt'] = hash_result[1]
        data['uuid'] = uuid.uuid4().hex
        data['registration_date'] = datetime.datetime.utcnow()

        try:
            return self.database.insert_into_db('user_info', data)
        except mysql.connector.Error() as e:
            print(f'Error: {e}')
