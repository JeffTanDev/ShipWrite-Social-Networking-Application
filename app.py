from flask import Flask
from flask import request, url_for, redirect, Blueprint, flash, jsonify
from flask import render_template

# will eventually help connect the different pages
bp = Blueprint('auth', __name__, url_prefix='/auth')

app = Flask(__name__)


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
    "123": {"password": "123"}
}


# Route to handle the login API (similar to the previous example)
@app.route('/api/login', methods=['POST'])
def login():
    username = request.form('username', '')
    password = request.form('password', '')

    if username in users and users['password'] == password:
        access_token = f"Bearer Token for {username}"
        response = {
            "access_token": access_token,
            "message": "Login success"
        }
        return jsonify(response), 200
    else:
        response = {"error": "Username or password incorrect"}
        return jsonify(response), 400

@app.route('/api/changepassword', methods=['POST'])
def change_password():
    username = data.get('username', '')
    email = data.get('email', '')
    password = data.get('password', '')
    if username in users and user[username]['email'] == email:
        access_token = f"Changepassword Token for {username}"
        response = {
            "access_token": access_token,
            "message": "Email been verified"
        }
        

        return jsonify(response), 200
    else:
        response = {"error": "username does not match with the email"}
        return jsonify(response), 400






# Route to handle the creation of a new account
@app.route('/api/newaccount', methods=['POST'])
def create_account():
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')
    firstname = data.get('firstname', '')
    lastname = data.get('lastname', '')
    email = data.get('email', '')
    phone = data.get('phone', '')

    # Check if the username or password is missing
    if not username or not password:
        return jsonify({"error": "Miss username or password"}), 400

    # Check if the username already exists
    if username in users:
        return jsonify({"error": "repeat username"}), 400

    # Create the new user account
    users[username] = {
        'password': password,
        'firstname': firstname,
        'lastname': lastname,
        'email': email,
        'phone': phone
    }
    print(users)

    return jsonify({"message": "Account created successfully"}), 200



if __name__ == '__main__':
    app.run()
