# import stuff of flask
from flask import render_template, request, redirect, url_for, flash, send_file, Blueprint

main_page = Blueprint('main_page', __name__)


# home page
@main_page.route("/")
def home():
    return render_template('index.html')


@main_page.route("/about")
def about():
    return render_template('about.html')

