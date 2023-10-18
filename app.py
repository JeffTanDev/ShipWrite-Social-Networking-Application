from flask import Flask
from flask import request, url_for, redirect, Blueprint, flash
from flask import render_template


#will eventually help connect the different pages
bp = Blueprint('auth', __name__, url_prefix='/auth')

app = Flask(__name__)


@app.route('/')
def start():
    #automatically redirects to login page upon app start up
    return redirect(url_for('login'))



@app.route('/login', methods=('GET', 'POST'))
# Logic for login page
def login():
    # open login page
    if request.method == 'POST':
        #If receiving a post from the frontend, store username and password data
        username = request.form['username']
        password = request.form['password']
        #database not connected
        #db = get_db()
        error = None

        #If username or password field is not filled, return an error
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        
        if error is None:
            #Here is where we send the info to the data base to see if the user exists
            #If user is verified redirect to home page
            return redirect(url_for(home_page))
            #if user doesn't exist redirect to register/create user page
            #If credentials are just wrong, raise error and reprompt login
            

        flash(error)

    return render_template('LogIn.html')


@app.route('/create_user', methods=('GET', 'POST'))
# Opens the create user page 
def create_user(name=None):
    #Works functionally the same to login but will perform different 
    #checks on the given username and password
    if request.method == 'POST':
        #If receiving a post from the frontend, store username and password data
        username = request.form['username']
        password = request.form['password']
        #database not connected
        #db = get_db()
        error = None

        #If username or password field is not filled, return an error
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        
        if error is None:
            #Here is where we send the info to the data base to see if the user exists
            #If username is not taken, store data in database and redirect to login
            #if username is taken, raise error and reprompt
            return redirect(url_for(login))

        flash(error)

    return render_template('CreateUser.html', name=name)


@app.route('/home_page', methods=('GET', 'POST'))
# Opens the home page 
def home_page(name=None):
    #This logic will be more complicated 
    return render_template('HomePage.html', name=name)




if __name__ == '__main__':
    app.run()
