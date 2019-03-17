import sqlite3
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, BooleanField
from wtforms.validators import DataRequired
from flask import Flask, render_template, redirect, session, jsonify
from flask import make_response
from flask import request


app = Flask(__name__)
app.config['SECRET_KEY'] = 'pokazeev'


@app.route('/', methods=['GET'])
def main_page():
    return render_template('main_page.html')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')


