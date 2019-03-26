import sqlite3
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, BooleanField,\
    SelectField, IntegerField, MultipleFileField, FileField
from wtforms.validators import DataRequired, length, NumberRange
from flask import Flask, render_template, redirect, session, jsonify
from flask import make_response
from flask import request
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pokazeev'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(80), unique=False, nullable=False)

    def __repr__(self):
        return '<UserModel {} {}>'.format(
            self.id, self.username, self.password_hash)


class ProductModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), unique=False, nullable=False)
    category = db.Column(db.String(100), unique=False, nullable=False)
    cost = db.Column(db.String(50), unique=False, nullable=False)
    count = db.Column(db.String(50), unique=False, nullable=False)
    s_description = db.Column(db.String(500), unique=False, nullable=False)
    b_description = db.Column(db.String(5000), unique=False, nullable=False)
    main_photo = db.Column(db.String(100), unique=False, nullable=True)




class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class NewProductForm(FlaskForm):
    category = SelectField('Languages', choices=[
        ('phones', 'Телефоны и аксессуары'), ('computers', 'Компьютеры и оргтехника'),
        ('electronics', 'Электроника'), ('appliances', 'Бытовая техника'), ('clothes', 'Одежда'),
        ('children', 'Все для детей'), ('clock', 'Бижутерия и часы'), ('bag', 'Сумки и обувь'),
        ('house', 'Для дома и сада'), ('car', 'Автотовары'), ('health', 'Красота и здоровье'),
        ('sport', 'Спорт и развлечение')])
    product_name = StringField('Название товара', validators=[DataRequired(), length(max=100)])
    cost = IntegerField('Цена', validators=[DataRequired(), NumberRange(0, 10**50)])
    count = IntegerField('Количество', validators=[DataRequired(), NumberRange(0, 10**50)])
    s_description = TextAreaField('Краткое описание', validators=[length(max=500)])
    b_description = TextAreaField('Полное описание', validators=[length(max=5000)])
    submit = SubmitField('Добавить')

db.create_all()


@app.route('/', methods=['GET'])
def main_page():
    return render_template('main_page.html')


@app.route('/categories/<category>')
def category_product(category):
    products = ProductModel.query.filter_by(category=category).all()[:100]

    return render_template('category_product.html', products=products)


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_in():
    form = LoginForm()
    form.username.errors = []
    form.submit.label.text = 'Зарегистрироваться'
    if form.validate_on_submit():
        user_name = form.username.data
        password = form.password.data
        try:
            user1 = UserModel(username=user_name, password_hash=generate_password_hash(password))
            db.session.add(user1)
            db.session.commit()
            session['username'] = user1.username
            session['user_id'] = user1.id
            return redirect("/lka")
        except Exception as e:
            form.username.errors = ['Данный пользователь уже существует']
            return render_template('authorization.html', name='Регистрация', form=form)
    return render_template('authorization.html', name='Регистрация', form=form, )


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_name = form.username.data
        password = form.password.data
        user = UserModel.query.filter_by(username=user_name).first()
        if user and check_password_hash(user.password_hash, password):
            session['username'] = user.username
            session['user_id'] = user.id
            return redirect("/lka")
        form.password.errors = ['Неверный пользователь или пароль']
    return render_template('authorization.html', name='Авторизация', form=form)


@app.route('/lka')
def lka():
    if 'username' not in session:
        return redirect('/login')
    return render_template('lka.html')


@app.route('/lka/new_product', methods=['GET', 'POST'])
def new_product():
    form = NewProductForm()
    if 'username' not in session or session['username'] != 'admin':
        return '''<h1>Доступ к странице закрыт</h1>'''
    else:
        if form.validate_on_submit():
            product = ProductModel(product_name=form.product_name.data, category=form.category.data,
                                   cost=form.cost.data, count=form.count.data,
                                   s_description=form.s_description.data,
                                   b_description=form.b_description.data)
            db.session.add(product)
            db.session.commit()
            path = os.path.join('static\\image\\', str(product.id))
            os.mkdir(path)
            files = request.files.getlist("files")
            for i in range(len(files)):
                end = files[i].filename.split('.')[-1]
                if end not in ['jpg', 'jpeg', 'png', 'bmp', 'raw', 'gif', 'psd', 'tiff']:
                    form.submit.errors = ['Неверный формат изображения']
                    return render_template('new_product.html', form=form)
                if i == 0:
                    product.main_photo = '\\' + path + \
                                         '\\0.' + files[i].filename.split('.')[-1]
                    db.session.commit()
                files[i].save(path + '\\' + str(i) + '.' + files[i].filename.split('.')[-1])
            return redirect('/lka')
        return render_template('new_product.html', form=form)
'''
product = ProductModel.query.filter_by(id=1).first()
db.session.delete(product)
db.session.commit()'''




if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')



'''Xiaomi Redmi 4A. Золотой цвет. Бюджетный смартфон. 2SIM. Android. Оперативная память: 2Гб. Основная память: 32Гб'''
'''Бренд:XIAOMI
Разблокировка телефона:Да
Режимы сети:2SIM/Multi-Bands
Поддерживаемый язык:Французский,Немецкий,Русский,Польский,Английский,Турецкий,Итальянский,Испанский,Португальский
Функция:HD-видеоплеер,Сообщения,Видеоплеер,Воспроизведение MP3,Слот для карт памяти,E-mail,Bluetooth,FM-радио,GPRS,Датчик гравитации,Сенсорный экран,Фронтальная камера,QWERTY-клавиатура,GPS-навигация,Wi-Fi
Состояние товара:Новый
Тип аккумулятора:Не съёмный
Год выпуска:2017
Тип сенсора экрана:Ёмкостный
Разрешение дисплея:1280x720
Производитель процессора:Qualcomm
Ёмкость аккумулятора:3120mAh(typ)
Фронтальная камера:5 Мп
Основная камера:13.0 Мп
Количество камер:1 основная + 1 фронтальная
Число ядер процессора:Четырёхъядерный
Оперативная память:2 Г
Операционная система:Android
Модель Xiaomi:Редми 4A 2 ГБ 32 ГБ
Цветность дисплея:Цвет
Разрешение видеозаписи:720 P
Стандарты связи:GSM/WCDMA/LTE
Размер дисплея:5.0
Количество SIM-карт:2
Дизайн:Моноблок
Толщина:Ультратонкий (< 9мм)
Размеры:139.5x8.5x70.4mm
Google Play :Да
Встроенная память:32 Г
Время разговора:About 6-8 hours
CPU:Snapdragon 425 Quad Core up to 1.4GHz
GPU:Adreno 308 , 500MHz
Camera:Back 13.0MP; 
Front 5.0MP
Screen:5.0" HD 1280x720pxOS:MIUI 8.1 Based on Android 6.0.12G:GSM B2/B3/B5/B83G:WCDMA B1/B2/B5/B84G:FDD-LTE B1/B3/B4/B5/B7/B20;TD-LTE B38/B40
Бренд:XIAOMI
Разблокировка телефона:Да
Режимы сети:2SIM/Multi-Bands
Поддерживаемый язык:Французский,Немецкий,Русский,Польский,Английский,Турецкий,Итальянский,Испанский,Португальский
Функция:HD-видеоплеер,Сообщения,Видеоплеер,Воспроизведение MP3,Слот для карт памяти,E-mail,Bluetooth,FM-радио,GPRS,Датчик гравитации,Сенсорный экран,Фронтальная камера,QWERTY-клавиатура,GPS-навигация,Wi-Fi
Состояние товара:Новый
Тип аккумулятора:Не съёмный
Год выпуска:2017
Тип сенсора экрана:Ёмкостный
Разрешение дисплея:1280x720
Производитель процессора:Qualcomm
Ёмкость аккумулятора:3120mAh(typ)
Фронтальная камера:5 Мп
Основная камера:13.0 Мп
Количество камер:1 основная + 1 фронтальная
Число ядер процессора:Четырёхъядерный
Оперативная память:2 Г
Операционная система:Android
Модель Xiaomi:Редми 4A 2 ГБ 32 ГБ
Цветность дисплея:Цвет
Разрешение видеозаписи:720 P
Стандарты связи:GSM/WCDMA/LTE
Размер дисплея:5.0
Количество SIM-карт:2
Дизайн:Моноблок
Толщина:Ультратонкий (< 9мм)
Размеры:139.5x8.5x70.4mm
Google Play :Да
Встроенная память:32 Г
Время разговора:About 6-8 hours
CPU:Snapdragon 425 Quad Core up to 1.4GHz
GPU:Adreno 308 , 500MHz
Camera:Back 13.0MP; 
Front 5.0MP'''