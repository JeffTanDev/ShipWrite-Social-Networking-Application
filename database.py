import mysql.connector
from datetime import datetime
from usermanager import UserManager
from connection_pool import ConnectionPool
import random


class DataBase:

    # Create pool of connections so they can be reused without having to open and close for each transaction
    def __init__(self, connection_pool) -> None:
        self.connection_pool = connection_pool
    
    def _execute_db_modification(self, modification_query: str, values: str=None) -> bool or None:
        try:
            with self.connection_pool.get_connection() as connection:
                with connection.cursor() as cursor:
                    if values is not None:
                        cursor.execute(modification_query, values)
                    else:
                        cursor.execute(modification_query)
                connection.commit()
                return True
        except mysql.connector.Error as e:
            raise e
    
    def _execute_db_read(self, read_query: str) -> list or None:
        try:
            with self.connection_pool.get_connection() as connection:
                with connection.cursor(dictionary=True) as cursor:
                    cursor.execute(read_query)
                    result = cursor.fetchall()
                return result
        except mysql.connector.Error as e:
            raise e

    def insert_into_db(self, table_name: str, data: dict) -> bool:
        """
        Insert a new record into a specified database table with the provided data.

        Args:
            table_name (str): The name of the table in which to insert the data.
            data (dict): A dictionary containing the column names as keys and their corresponding
                values for the new record.

        Returns:
            bool: True if the insertion is successful, False otherwise.

        Example: insert_into_db("user_info", {'first_name': 'Jesse', 'last_name': 'Baxter' ... etc})

        """
        insert_query = f"INSERT INTO {table_name} ({', '.join(data.keys())}) VALUES ({', '.join(['%s' for _ in data])})"
        values = tuple(data.values())
        return self._execute_db_modification(insert_query, values)


    def read_from_db(self, table_name: str, data: dict) -> list:
        """
        Retrieve data from a specified database table using a SELECT query.

        Args:
            table_name (str): The name of the table from which to retrieve data.
            data (dict): A dictionary containing the following keys:
                - 'fields' (list): A list of column names to select.
                - 'formatting' (str, optional): Additional SQL formatting, such as WHERE clauses,
                JOIN statements, or ORDER BY clauses. If not provided, the query will select all records.

        Returns:
            list or None: A list of dictionaries representing the selected records with the columns being the keys. Returns None if an error occurs.

        Example of a call: select_from_db("user_info", {"fields": ["first_name"], "formatting": None})

        Example of getting something out of the return value:
            names = DataBase.select_from_db("user_info", {"fields": ["first_name"], "formatting": None})

            if names:
                for entry in names:
                    print(f"{entry['first_name']} is in the database!")

        """
        read_query = f"SELECT {', '.join(data['fields'])} FROM {table_name} {data['formatting'] if data['formatting'] else ''}"
        return self._execute_db_read(read_query)

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

        IMPORTANT:
            - There must be some kind of formatting passed in. You cannot edit a record without narrowing it down on some condition.
              If you do not pass a format string in the modification will change the value in the column for every single record.
        """

        if formatting is None or formatting == '':
            return False

        update_k_v_pairs = ', '.join([f'{key}="{data[key]}"'for key in data])
        update_query = f"UPDATE {table_name} SET {update_k_v_pairs} {formatting}"
        return self._execute_db_modification(update_query)

    def update_times_viewed(self, ocean_messageID: int) -> bool:
        update_query = f"UPDATE ocean_messages SET times_viewed=times_viewed + 1 WHERE ocean_messageID={ocean_messageID}"
        return self._execute_db_modification(update_query)


    def select_ocean_bottle(self, user_id):
        """
        Select a bottle from the ocean with weighted chance.

        Args:
            user_id: The current user's ID, so we don't return a user's own bottle

        Returns:
            list: The list of values from the database associated with the message

        IMPORTANT:
        """

        select_formatting = f"LEFT JOIN viewed_ocean_messages vom ON om.ocean_messageID=vom.ocean_messageID WHERE om.user_id != {user_id}\
                            AND om.ocean_messageID NOT IN (SELECT DISTINCT ocean_messageID FROM viewed_ocean_messages WHERE user_ID= {user_id})\
                            GROUP BY om.ocean_messageID ORDER BY times_viewed DESC LIMIT 100;"

        ocean_bottles = self.read_from_db('ocean_messages om', {'fields': ['om.*, vom.time_viewed'], 'formatting': f"{select_formatting}"})

        if not ocean_bottles:
            return None
        
        # Will be used for weighted random selection
        raw_bottle_weights = []
        for bottle in ocean_bottles:
            selected_chance = 1.0
            views = bottle['times_viewed']
            selected_chance *= 1/ (views + 1)

            # Find the time the bottle was last viewed
            # Don't use time_sent because that is the overall age of the bottle and could be days/weeks/months
            time_stamp_from_db = bottle['time_viewed']
            
            if time_stamp_from_db:
                age_minutes = (datetime.utcnow() - time_stamp_from_db).total_seconds() / 60
            else:
                age_minutes = 0

            if age_minutes != 0:
                selected_chance += age_minutes / 360
            
            raw_bottle_weights.append(selected_chance)
            
        weight_total = sum(raw_bottle_weights)

        # Normalize vector of weights to equal 1.0 (probability should add up to one)
        norm_bottle_weights = [w / weight_total for w in raw_bottle_weights]
        return random.choices(ocean_bottles, norm_bottle_weights, k=1)[0]
    

    def get_pending_friends(self, userID: int) -> dict:
        try:
            added_by_user = self._execute_db_read(f'SELECT fr.user2_ID, fr.creation_date, ui.first_name FROM friendship fr JOIN user_info ui ON fr.user2_ID = ui.user_ID WHERE user1_ID = {userID} and status = "PENDING"')
            added_user = self._execute_db_read(f'SELECT fr.user1_ID, fr.creation_date, ui.first_name FROM friendship fr JOIN user_info ui ON fr.user1_ID = ui.user_ID WHERE user2_ID = {userID} and status = "PENDING"')
            result = {'user_added': added_by_user, 'added_user': added_user}
            return result
        except mysql.connector.Error as e:
            return None
    
    def get_all_friends(self, userID: int) -> dict:
        try:
            user_friend_query = f"SELECT fr.creation_date, ui.first_name, ui.last_name FROM friendship fr JOIN user_info ui ON ui.user_ID = fr.user2_ID WHERE user1_ID={userID} AND fr.status = 'ACCEPTED'"
            user_friends = self._execute_db_read(user_friend_query)
            return user_friends
        except mysql.connector.Error as e:
            return None

