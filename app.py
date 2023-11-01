from flask import Flask
from flask import request, url_for, redirect, Blueprint, flash, jsonify, make_response
from flask import render_template
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from database import DataBase
from usermanager import UserManager
from decouple import config
from datetime import datetime

# will eventually help connect the different pages
bp = Blueprint('auth', __name__, url_prefix='/auth')

app = Flask(__name__)
# app.config['JWT_SECRET_KEY'] = config('JWT_KEY')
app.config['JWT_SECRET_KEY'] = config('JWT_KEY', default='YourDefaultSecretKey')
jwt = JWTManager(app)
database = DataBase()
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


# Mock user data (replace this with a proper authentication system)
users = {
    "user1": {"password": "12345"},
    "123": {"password": "123", "email": "123@example.com", "firstname": "Haoyang", "lastname": "Tan"}
}


# Route to handle the login API (similar to the previous example)
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()

    if usermanager.check_password(data['password'], data['username']):
        access_token = create_access_token(identity=data['username'])
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"error": "Username or password incorrect"}), 400


# Route to handle the change password API
@app.route('/api/changepassword', methods=['POST'])
def change_password():
    data = request.get_json()
    username = data.get('username', '')
    email = data.get('email', '')
    password = data.get('password', '')
    passwordcheck = data.get('passwordcheck', '')
    if username in users and users[username]['email'] == email:
        if (password == passwordcheck) and (not (users[username]['password'] == password)):
            users[username]['password'] = password
            access_token = f"Bearer Token for {username}"
            response = {
                "access_token": access_token,
                "message": "Change success"
            }
            return jsonify(response), 200
        elif users[username]['password'] == password:
            response = {"error": "password is the same with the used one"}
            return jsonify(response), 400
        else:
            response = {"error": "Two new passwod need be the same!"}
            return jsonify(response), 400
    else:
        response = {"error": "Username does not match with this email"}
        return jsonify(response), 400


@app.route('/api/updateuserinfo', methods=['POST'])
@jwt_required()
def update_user_info():
    current_user = get_jwt_identity()  # get current user name
    data = request.get_json()

    # update dictionary
    fields_to_update = {k: v for k, v in data.items() if k in ["first_name", "last_name", "email", "phone"]}

    if not fields_to_update:
        return jsonify({"error": "No valid fields provided for update"}), 400

    # update database
    update_result = database.update_values_in_db("user_info", fields_to_update, f"WHERE username = '{current_user}'")

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
    # Retrieve the identity from the JWT token (here, it's the username)
    current_user = get_jwt_identity()

    # Construct the query
    user_data = {
        "fields": ["username", "first_name", "last_name", "email", "phone"],
        "formatting": f"WHERE username = '{current_user}'"
    }

    # Retrieve user information from the database
    user_info = database.select_from_db("user_info", user_data)

    # Check if user information was successfully retrieved
    if user_info and len(user_info) > 0:
        user_info = user_info[0]  # Get the first matching record
        return jsonify(username=user_info[0],
                       first_name=user_info[1],
                       last_name=user_info[2],
                       email=user_info[3],
                       phone=user_info[4]), 200
    else:
        return jsonify(error="User not found"), 404

@app.route('/api/bottlemessages/send', methods=['POST'])
@jwt_required()
def send_message():
    data = request.get_json()
    message_content = data.get('message')
    current_user = get_jwt_identity()

    # find user ID
    user_info = database.select_from_db("user_info", {
        "fields": ["user_id"],
        "formatting": f"WHERE username = '{current_user}'"
    })

    if user_info and len(user_info) > 0:
        user_id = user_info[0][0]  # Get user ID
        time_sent = datetime.now()  # current time stamp

        # save bottle to database
        database.insert_into_db("ocean_messages", {
            "user_id": user_id,
            "time_sent": time_sent,
            "message_content": message_content
        })
        return jsonify({"message": "Message sent successfully"}), 200
    else:
        return jsonify({"error": "User not found"}), 404


@app.route('/api/bottlemessages', methods=['GET'])
def get_bottle_message():
    db = DataBase()  # 根据您的实际代码结构创建 DataBase 实例
    message = db.get_random_message()

    if message:
        return jsonify({"message_content": message[1]}), 200  # 假设消息内容在第二个字段
    else:
        return jsonify({"error": "No messages found"}), 404


if __name__ == '__main__':
    app.run()
