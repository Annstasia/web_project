import sqlite3
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, BooleanField
from wtforms.validators import DataRequired
from flask import Flask, render_template, redirect, session, jsonify
from flask import make_response
from flask import request


class DB:
    def __init__(self):
        self.conn = sqlite3.connect('news.db', check_same_thread=False)

    def get_connection(self):
        return self.conn

    def __del__(self):
        self.conn.close()


class UserModel:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_name VARCHAR(50),
                            password_hash VARCHAR(120))''')
        cursor.close()
        self.connection.commit()

    def insert(self, user_name, password_hash):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO users
                            (user_name, password_hash)
                            VALUES (?,?)''', (user_name, password_hash))
        cursor.close()
        self.connection.commit()

    def exists(self, user_name, password_hash):

        cursor = self.connection.cursor()
        cursor.execute('''SELECT * FROM users WHERE user_name = ? AND password_hash = ?''',
                       (user_name, password_hash))
        row = cursor.fetchone()
        cursor.close()
        return (True, row[0]) if row else (False,)

    def get(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute('''SELECT * FROM users WHERE id = ?''', (str(user_id)))
        row = cursor.fetchone()
        cursor.close()
        return row

    def get_all(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        return rows


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


app = Flask(__name__)
app.config['SECRET_KEY'] = 'pokazeev'
db = DB()
UserModel(db.get_connection()).init_table()


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


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_in():
    form = LoginForm()
    form.submit.label.text = 'Зарегистрироваться'
    if form.validate_on_submit():
        user_name = form.username.data
        password = form.password.data
        user_model = UserModel(db.get_connection())
        exists = user_model.exists(user_name, password)
        if exists[0]:
            return render_template('sign_up_error.html',  name='Регистрация', form=form)
        UserModel(db.get_connection()).insert(user_name, password)
        session['username'] = user_name
        session['user_id'] = user_model.exists(user_name, password)[1]
        return redirect("/lka")
    return render_template('authorization.html', name='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_name = form.username.data
        password = form.password.data
        user_model = UserModel(db.get_connection())
        exists = user_model.exists(user_name, password)
        if exists[0]:
            session['username'] = user_name
            session['user_id'] = exists[1]
        print('hkjhjkhk')
        return redirect("/lka")
    return render_template('authorization.html', name='Авторизация', form=form)


@app.route('/lka')
def lka():
    if 'username' not in session:
        return redirect('/login')
    return render_template('lka.html')


@app.route('/lka/new_product', methods=['GET', 'POST'])
def new_product():
    if 'username' not in session or session['username'] != 'admin':
        return '''<h1>Доступ к странице закрыт</h1>'''
    else:
        if request.method == 'GET':
            return render_template('new_product.html')
        elif request.method == 'POST':
            print(request.form.get('name'))
            print(request.form.get('category'))
            print(request.form.get('cost'))
            print(request.form.get('s-description'))
            print(request.form.get('b-description'))
            print(request.form['file'])



if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')


