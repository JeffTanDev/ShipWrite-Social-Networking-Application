import mysql.connector
import uuid
import bcrypt
from datetime import datetime


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

    def hash_password(self, password: str) -> tuple:
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

    def update_password(self, data: dict) -> bool:
        """
        Update the password and password salt in the provided data dictionary with new hashed values.

        Args:
            data (dict): A dictionary containing user data, including the "password" to be hashed.

        Returns:
            bool: True if the password and password salt were successfully updated, False otherwise.

        This method takes a dictionary of user data as input and updates the "password" and "password_salt"
        values in the dictionary with new hashed values. The updated values are obtained by calling the
        `hash_password` method, which returns a tuple of bytes-like objects representing the hashed
        password and password salt. This method then decodes these byte-like objects to UTF-8 strings
        and updates the data dictionary.

        If the password hashing process is successful, the method returns True. If an exception is raised
        during the process, it returns False, indicating that the update was not successful.
        """
        try:
            new_password_info = self.hash_password(data["password"])
            data["password"] = new_password_info[0].decode('utf-8')
            data["password_salt"] = new_password_info[1].decode('utf-8')
            return True
        except:
            return False

    def check_password(self, password: str, username: str) -> bool:
        """
        Check if a provided password matches the stored password for a given username.

        Args:
            password (str): The plaintext password to be checked.
            username (str): The username associated with the stored password.

        Returns:
            bool: True if the password is correct; False otherwise.
        """

        stored_info = self.database.read_from_db('user_info', {'fields': ['password', 'password_salt'], 'formatting': f'WHERE username = "{username}"'})
        
        if stored_info:
            rehashed_password = bcrypt.hashpw(password.encode('utf-8'), stored_info[0]['password_salt'].encode('utf-8'))
            return rehashed_password.decode("utf-8") == stored_info[0]['password']
        else:
            return False

    def check_username(self, username: str) -> bool:
        """
        Check if a username exists in the user database.

        Args:
            username (str): The username to be checked for existence.

        Returns:
            bool: True if the username exists in the database; False otherwise.
        """

        query_result = self.database.read_from_db('user_info', {'fields': [
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
        data['registration_date'] = datetime.utcnow()

        try:
            return self.database.insert_into_db('user_info', data)
        except mysql.connector.Error() as e:
            print(f'Error: {e}')
    
    def create_friendship(self, requesterID: int, recieverID: int) -> bool | None:
        """
        Create record in the database table with the provided data.

        Args:
            requesterID (int): ID of person sending request
            recieverID (int): ID of person getting request

        Creates  requester -> reciever and reciever -> requester rows in friendship table
        Returns:
            bool: True if the update was successful, raises an error otherwise.
        """
        if not requesterID or not recieverID or requesterID == recieverID:
            return False
        
        new_friendship_query = 'INSERT into friendship(user1_ID, user2_ID, status, creation_date) VALUES(%s, %s, %s, %s), (%s, %s, %s, %s)'
        # A->B friendship row ends with timestamp, then B->A friendship
        values = [requesterID, recieverID, "ACCEPTED", datetime.utcnow(), recieverID, requesterID, "PENDING", datetime.utcnow()]
        return self.database._execute_db_modification(new_friendship_query, values)
    

    def delete_friendship(self, userID: int, friendID: int) -> bool | None:
        """
        Remove records in the database table with the provided data.

        Args:
            userID (int): ID of person requesting deletion
            friendID (int): ID of friend getting deleted

        Removes  user -> friend and friend -> user rows in friendship table
        Returns:
            bool: True if the update was successful, raises an error otherwise.
        """
        if not userID or not friendID or userID == friendID:
            return False
        
        accept_friendship_query = f'DELETE FROM friendship WHERE user1_ID={userID} OR user1_ID={friendID} AND user2_ID={friendID} or user2_ID={userID}'
        return self.database._execute_db_modification(accept_friendship_query)


    def accept_friend_request(self, userID: int, friendID: int) -> bool | None:
        """
        Update record in the database table with the provided data.

        Args:
            userID (int): ID of person accepting request
            friendID (int): ID of person who sent request

        Returns:
            bool: True if the update was successful, raises an error otherwise.
        """
        if not userID or not friendID or userID == friendID:
            return False
        
        accept_friendship_query = f'UPDATE friendship SET status="ACCEPTED" WHERE user1_id ={userID} AND user2_id={friendID}'
        return self.database._execute_db_modification(accept_friendship_query)


    def decline_friend_request(self, userID: int, friendID: int) -> bool | None:
        """
        Update record in the database table with the provided data.

        Args:
            userID (int): ID of person accepting request
            friendID (int): ID of person who sent request

        Removes friendship from table
        Returns:
            bool: True if the update was successful, raises an error otherwise.
        """
        if not userID or not friendID or userID == friendID:
            return False
        
        return self.database.delete_friendship(userID, friendID)
