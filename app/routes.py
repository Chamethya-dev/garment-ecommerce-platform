from flask import Blueprint, render_template
from flask_login import login_required

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/home')
@login_required # Forces user to be logged in to see the home page
def home():
    return render_template('home.html')