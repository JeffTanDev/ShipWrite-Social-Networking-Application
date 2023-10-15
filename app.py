from flask import Flask
from flask import request, url_for, redirect, Blueprint
from flask import render_template


#will eventually help connect the different pages
bp = Blueprint('auth', __name__, url_prefix='/auth')

app = Flask(__name__)


@app.route('/')
def start():
    return redirect(url_for('login'))

@app.route('/login', methods=('GET', 'POST'))
# Opens the login page 
def login():
    if request.method == 'POST':
        return redirect('CreateUser.html')
    
    return render_template('LogIn.html')


@app.route('/create_user', methods=('GET', 'POST'))
# Opens the create user page 
def open_create_user(name=None):
    return render_template('CreateUser.html', name=name)


@app.route('/home_page', methods=('GET', 'POST'))
# Opens the home page 
def open_home_page(name=None):
    return render_template('HomePage.html', name=name)




if __name__ == '__main__':
    app.run()
