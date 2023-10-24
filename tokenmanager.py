import jwt
import datetime
from decouple import config


class TokenManager():
    """
    A class for managing JWT tokens for user authentication and session management.

    Args:
        database: An instance of a database manager to perform database operations.

    Attributes:
        database: The database manager for retrieving user information.
        secret_key (str): The secret key used to sign and verify JWT tokens.
        algorithm (str): The algorithm used for JWT token encoding and decoding.

    """

    def __init__(self, database) -> None:
        """
        Initializes a TokenManager instance.

        Args:
            database: An instance of a database manager to perform database operations.

        """

        self.database = database
        self.secret_key = config('TOKEN_SECRET')
        self.algorithm = config('TOKEN_ALG')

    def create_token(self, username: str) -> str:
        """
        Create a JWT token for the provided username.

        Args:
            username (str): The username for which the token is generated.

        Returns:
            str: The generated JWT token.

        """

        user_info = self.database.select_from_db('user_info', {'fields': ['user_ID', 'username'],
                                                               'formatting': f'WHERE username = "{username}"'})
        try:
            user_ID = user_info[0][0]
            username = user_info[0][1]
            package = {"user_id": user_ID,
                       "username": username,
                       "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)}
            token = jwt.encode(package, self.secret_key,
                               algorithm=self.algorithm)
            return token
        except:
            print("Error creating Token!")

    def decode_token(self, token: str) -> dict:
        """
        Decode and verify a JWT token.

        Args:
            token (str): The JWT token to decode and verify.

        Returns:
            dict: The decoded token's payload if valid; None if the token is expired or invalid.

        """

        try:
            package = jwt.decode(token, self.secret_key,
                                 algorithms=self.algorithm)
            return package
        except jwt.ExpiredSignatureError:
            return None

    def extend_token_expiration(self, token: str) -> str:
        package = self.decode_token(token)

        if package:
            expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            package['exp'] = expiration
            new_token = jwt.encode(package, self.secret_key, self.algorithm)
            return new_token
        else:
            return None
