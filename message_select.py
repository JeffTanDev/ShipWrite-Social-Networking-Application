import database
import app
import mysql.connector
from mysql.connector import pooling
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity


def select_message():
    # Algorithm to select a message to ensure messages are responded to 
    # and older messages are not forgotten

    # Messages with no responses can be given a base chance of selection
    # either 100% or some other really high percent chance to garuntee they get responded to

    # If an age is added to messages, that can also be used to help increase the 
    # chance of selection; older the message, higher the chance
    current_userID = get_jwt_identity()
    connection = database.connection_pool.get_connection()
    if connection is None:
        print("Database connection is not available.")
        return None
    # Query the database for up to 100 messages and order them by the number of times viewed 
    # That is not also written by the current user

    '''
    if ocean_messages empty(No unviewed messages):
        query = "SELECT * FROM viewed_ocean_messages\
                WHERE NOT user_id = 'current_userID'\
                ORDER times_viewed\
                LIMIT 100;"
    else:
    '''
    query = "SELECT * FROM ocean_messages\
            WHERE NOT user_id = 'current_userID'\
            ORDER times_viewed\
            LIMIT 100;"
    

    try:
        with connection.cursor() as cursor:
            #execute the query
            cursor.execute(query)
            #fetch the first message from the query(The least viewed)
            message = cursor.fetchone()
            return message
    except mysql.connector.Error as e:
        print(f"Error: {e}")
        return None
    finally:
        connection.close()


    # As the number of responses increases on a message, the chance can be diminshed
    # to help messages with fewer responses get noticed first

    

    # Can prioritize nearby messages by using inverses to represent a percent chance
    # of being chosen
    # Ex: bottle 1 is 2 miles away; bottle 2 is 20 miles away
    # bottle one is given a .5% or 50% chance(1/2)
    # bottle 2 is given a .05% or 5% chance(1/20)
    # possible to add other variables to the chance to edit the chance of selection
    # Messages have lat and long but users don't to compare to
    return message