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


@app.route('/phone_and_accessories')
def phone_and_accessories():
    return '''<h1>SDGGERH</h1>'''


@app.route('/computers')
def computers():
    return '''<h1>SDGGERH</h1>'''


@app.route('/electronics')
def electronics():
    return '''<h1>SDGGERH</h1>'''


@app.route('/appliances')
def appliances():
    return '''<h1>SDGGERH</h1>'''


@app.route('/clothes')
def clothes():
    return '''<h1>SDGGERH</h1>'''


@app.route('/children')
def children():
    return '''<h1>SDGGERH</h1>'''


@app.route('/bijouterie_and_clocks')
def bijouterie_and_clocks():
    return '''<h1>SDGGERH</h1>'''


@app.route('/bags_and_shoes')
def bags_and_shoes():
    return '''<h1>SDGGERH</h1>'''


@app.route('/house_and_garden')
def house_and_garden():
    return '''<h1>SDGGERH</h1>'''


@app.route('/auto_products')
def auto_products():
    return '''<h1>SDGGERH</h1>'''


@app.route('/beauty_and_health')
def beauty_and_health():
    return '''<h1>SDGGERH</h1>'''


@app.route('/sport_and_entartainment')
def sport_and_entertainment():
    return '''<h1>SDGGERH</h1>'''


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')


