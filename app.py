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

# Mock user data (replace this with a proper authentication system)
users = {
    "user1": "password1",
    "user2": "password2"
}

# Route to handle the login API (similar to the previous example)
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')

    if username in users and users[username] == password:
        access_token = f"Bearer Token for {username}"
        response = {
            "access_token": access_token,
            "message": "登录成功"
        }
        return jsonify(response), 200
    else:
        response = {"error": "Username or password incorrect"}
        return jsonify(response), 400


@app.route('/create_user', methods=('GET', 'POST'))
# Opens the create user page 
def create_user(name=None):
    # Works functionally the same to login but will perform different
    # checks on the given username and password
    if request.method == 'POST':
        # If receiving a post from the frontend, store username and password data
        username = request.form['username']
        password = request.form['password']
        # database not connected
        # db = get_db()
        error = None

        # If username or password field is not filled, return an error
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            # Here is where we send the info to the data base to see if the user exists
            # If username is not taken, store data in database and redirect to login
            # if username is taken, raise error and reprompt
            return redirect(url_for(login))

        flash(error)

    return render_template('CreateUser.html', name=name)


@app.route('/homepage', methods=('GET', 'POST'))
# Opens the home page 
def home_page(name=None):
    # This logic will be more complicated
    return render_template('HomePage.html', name=name)


if __name__ == '__main__':
    app.run()
