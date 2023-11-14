from flask import Flask
from flask import request, url_for, redirect, Blueprint, flash, jsonify, make_response
from flask import render_template
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, create_refresh_token
from connection_pool import ConnectionPool
from database import DataBase
from usermanager import UserManager
from decouple import config
from datetime import datetime, timedelta
from datetime import datetime
import threading


# will eventually help connect the different pages
bp = Blueprint('auth', __name__, url_prefix='/auth')
app = Flask(__name__)
# app.config['JWT_SECRET_KEY'] = config('JWT_KEY')
app.config['JWT_SECRET_KEY'] = config(
    'JWT_KEY', default='YourDefaultSecretKey')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(minutes=30)
jwt = JWTManager(app)
connection_pool = ConnectionPool.create_pool(10)
database = DataBase(connection_pool)
usermanager = UserManager(database)


# Define a root route to load the LogIn.html page
@app.route('/')
def root():
    return render_template('LogIn.html')


@app.route('/homepage')
# Opens the home page
def home_page(name=None):
    return render_template('HomePage.html', name=name)


@app.route('/createuser')
# Opens the CreateUser page
def create_user(name=None):
    return render_template('CreateUser.html', name=name)


@app.route('/profile')
# Opens the Profile page
def profile(name=None):
    return render_template('Profile.html', name=name)


@app.route('/edition')
# Opens the edition page
def edition(name=None):
    return render_template('Edition.html', name=name)


@app.route('/ocean')
# Opens the ocean page
def ocean(name=None):
    return render_template('Ocean.html', name=name)


@app.route('/bottlehistory')
# Opens the bottlehistory page
def bottlehistory(name=None):
    return render_template('BottleHistory.html', name=name)


@app.route('/api/token/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_userID = get_jwt_identity()
    new_access_token = create_access_token(identity=current_userID)
    new_refresh_token = create_refresh_token(identity=current_userID)
    return jsonify(access_token=new_access_token, refresh_token=new_refresh_token), 200


# Route to handle the login API (similar to the previous example)
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()

    if usermanager.check_password(data['password'], data['username']):
        user_info = database.read_from_db("user_info", {
            "fields": ["user_id"],
            "formatting": f"WHERE username ='{data['username']}'"
        })
        access_token = create_access_token(identity=user_info[0]['user_id'])
        refresh_token = create_refresh_token(identity=user_info[0]['user_id'])
        return jsonify(access_token=access_token, refresh_token=refresh_token), 200
    else:
        return jsonify({"error": "Username or password incorrect"}), 400


@app.route('/api/updateuserinfo', methods=['POST'])
@jwt_required()
def update_user_info():
    current_userID = get_jwt_identity()  # get current user name
    data = request.get_json()

    # update dictionary
    fields_to_update = {k: v for k, v in data.items() if k in ["first_name", "last_name", "email", "phone", "password"]}

    if not fields_to_update:
        return jsonify({"error": "No valid fields provided for update"}), 400

    if 'password' in fields_to_update.keys():
        usermanager.update_password(fields_to_update)

    # update database
    update_result = database.update_values_in_db("user_info", fields_to_update, f"WHERE user_ID = '{current_userID}'")

    if update_result:
        return jsonify({"message": "User info updated successfully"}), 200
    else:
        return jsonify({"error": "Failed to update user info"}), 500


# Route to handle the creation of a new account
@app.route('/api/newaccount', methods=['POST'])
def create_account():
    data = request.get_json()

    # Check if the username or password is missing
    if not data['username'] or not data['password']:
        return jsonify({"Error": "Missing username or password"}), 400

    # Check if the username already exists
    if usermanager.check_username(data['username']):
        return jsonify({"Error": "Username already taken"}), 400

    # Create the new user account
    if usermanager.create_user(data):
        return jsonify({"message": "Account created successfully"}), 200
    else:
        return jsonify({"message": "There was an error creating the account, please try again."}), 400


@app.route('/api/userinfo', methods=['GET'])
@jwt_required()
def get_user_info():
    # Retrieve the identity from the JWT token (here, it's the user ID)
    current_userID = get_jwt_identity()

    # Construct the query
    user_data = {
        "fields": ["username", "first_name", "last_name", "email", "phone"],
        "formatting": f"WHERE user_ID ='{current_userID}'"
    }

    # Retrieve user information from the database
    user_info = database.read_from_db("user_info", user_data)

    # Check if user information was successfully retrieved
    if user_info and len(user_info) > 0:
        user_info = user_info[0]  # Get the first matching record
        return jsonify(username=user_info['username'],
                       first_name=user_info['first_name'],
                       last_name=user_info['last_name'],
                       email=user_info['email'],
                       phone=user_info['phone']), 200
    else:
        return jsonify(error="User not found"), 404


@app.route('/api/bottlemessages/send', methods=['POST'])
@jwt_required()
def send_message():
    data = request.get_json()
    message_content = data.get('message')
    current_userID = get_jwt_identity()

    # Get Insert Query Ready
    message_data = {
        "user_id": current_userID,
        "time_sent": datetime.utcnow(),
        "message_content": message_content
    }

    # save bottle to database
    if database.insert_into_db("ocean_messages", message_data):
        return jsonify({"message": "Message sent successfully"}), 200
    else:
        return jsonify({"error": "User not found"}), 404


@app.route('/api/bottlemessages', methods=['GET'])
@jwt_required()
def get_bottle_message():
    current_userID = get_jwt_identity()
    message = database.select_ocean_bottle(current_userID)

    if message:
        message_id = message['ocean_messageID'] 
        
        # Essentially transforming this part into an async call to the inserts
        # Prior to switching to seperate thread get time was an average of 1681 ms over 100 requests
        # After the change the average get time is about 95 ms over 100 requests
        def perform_inserts():
            database.insert_into_db('viewed_ocean_messages', {'ocean_messageID': message_id, 'user_ID': current_userID, 'time_viewed': datetime.utcnow()})
            database.update_times_viewed(message_id)
        
        insert_thread = threading.Thread(target=perform_inserts)
        insert_thread.start()

        return jsonify({"message_content": message['message_content'], "message_ID": message_id}), 200
    else:
        return jsonify({"error": "No messages found"}), 404


@app.route('/api/bottlemessage/dropped', methods=['POST'])
@jwt_required()
def get_dropped_bottles():
    current_userID = get_jwt_identity()
    data = request.get_json()

    if data['time']:
        requested_time_tz_format = datetime.strptime(data['time'], '%Y-%m-%dT%H:%M:%S.%fZ')
        cut_off_time = requested_time_tz_format.strftime('%y-%m-%d %H:%M:%S')
    else:
        cut_off_time = datetime.strftime(datetime.now(), '%y-%m-%d %H:%M:%S')

    # Get up to 10 bottles dropped by the user
    # cut_off_time is in place so that if the user has 10+ messages we load the first ten and then
    # if it is requested to load more hit the route again but set the cut_off_time to be that of the oldest curently held message
    dropped_bottles = database.read_from_db('ocean_messages', 
                                              {'fields': ['ocean_messageID', 'time_sent', 'message_content'], 
                                               'formatting': 
                                               f"WHERE user_ID = {current_userID} AND time_sent <'{cut_off_time}' ORDER BY time_sent DESC LIMIT 10"})
    
    if dropped_bottles or dropped_bottles == []:
        return jsonify({"dropped_bottles": dropped_bottles}), 200
    else:
        return jsonify({"error": "No bottles dropped so far!"}), 400


@app.route('/api/bottlemessage/<messageID>/addreply', methods=['POST'])
@jwt_required()
def add_bottle_reply(messageID):
    current_userID = get_jwt_identity()
    data = request.get_json()
    
    reply_inserted = database.insert_into_db('ocean_message_replies', 
                                             {'ocean_messageID': messageID, 'user_ID': current_userID, 'reply_content': data['content'], 'time_added': datetime.utcnow()})

    if reply_inserted:
        return jsonify({"message": "Reply added sucessfully!"}), 200
    else:
        return jsonify({"message": "There was an error adding the reply, please try again."}), 400


@app.route('/api/bottlemessage/<messageID>/replies', methods=['POST'])
def view_bottle_replies(messageID):
    data = request.get_json()

    if data['time']:
        cut_off_time = data['time']
    else:
        cut_off_time = datetime.utcnow()

    # Get up to 10 replies on a particular bottle
    # cut_off_time is in place so that if the bottle has 10+ replies we load the first ten and then
    # if it is requested to load more hit the route again but set the cut_off_time to be that of the oldest curently held message
    bottle_replies = database.read_from_db('ocean_message_replies', 
                                              {'fields': ['replyID', 'reply_content', 'time_added'], 
                                               'formatting': 
                                               f"WHERE ocean_messageID = {messageID} AND time_added <'{cut_off_time}' ORDER BY time_added DESC LIMIT 10"})

    if bottle_replies:
        return jsonify({"bottle_replies": bottle_replies}), 200
    else:
        return jsonify({"error": "No replies so far!"}), 400


if __name__ == '__main__':
    app.run()
