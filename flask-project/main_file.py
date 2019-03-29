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


class BasketModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, unique=False, nullable=False)
    user_id = db.Column(db.Integer, unique=False, nullable=False)


class OrderModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, unique=False, nullable=False)
    user_id = db.Column(db.Integer, unique=False, nullable=False)



class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class NewProductForm(FlaskForm):
    category = SelectField('Categories', choices=[
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


class RedactionProductForm(FlaskForm):
    category = SelectField('Categories', choices=[
        ('phones', 'Телефоны и аксессуары'), ('computers', 'Компьютеры и оргтехника'),
        ('electronics', 'Электроника'), ('appliances', 'Бытовая техника'), ('clothes', 'Одежда'),
        ('children', 'Все для детей'), ('clock', 'Бижутерия и часы'), ('bag', 'Сумки и обувь'),
        ('house', 'Для дома и сада'), ('car', 'Автотовары'), ('health', 'Красота и здоровье'),
        ('sport', 'Спорт и развлечение')])
    product_name = StringField('Измененное название', validators=[length(max=100)])
    cost = IntegerField('Новая цена', validators=[NumberRange(0, 10 ** 50)])
    count = IntegerField('Новое количество', validators=[NumberRange(0, 10 ** 50)])
    s_description = TextAreaField('Новое краткое описание', validators=[length(max=500)])
    b_description = TextAreaField('Новое полное описание', validators=[length(max=5000)])
    submit = SubmitField('Добавить')


def find_asked_name(name, ask):
    print(name)
    nameList = name.lover().split()
    askList = ask.lover().split()
    count = 0
    for i in nameList:
        for j in askList:
            if i == j:
                count += 1
    return count


db.create_all()


@app.route('/', methods=['GET', 'POST'])
def main_page():
    if request.method == 'GET':
        return render_template('main_page.html')
    elif request.method == 'POST' and request.form.get('ask', False):
        return redirect('/all/' + request.form['ask'])


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



@app.route('/logout')
def logout():
    session.pop('username',0)
    session.pop('user_id',0)
    return redirect('/login')


@app.route('/lka', methods=['POST', 'GET'])
def lka():
    if 'username' not in session:
        return redirect('/login')
    basket_products = [ProductModel.query.filter_by(id=i.product_id).first()
                       for i in BasketModel.query.filter_by(user_id=session['user_id']).all()]

    if request.method == 'POST':
        print(i for i in request.form)
        for i in basket_products:
            print(i)
            if request.form.get(str(i.id), None) == str(i.id):
                print(i.id)
                return redirect('/pay/' + str(i.id))
    if request.method == 'GET':

        order_products = [ProductModel.query.filter_by(id=i.product_id).first()
                         for i in OrderModel.query.filter_by(user_id=session['user_id']).all()]
        return render_template('lka.html', basket_products=basket_products, order_products=order_products)


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
                    product.main_photo = '\\' + path + '\\0.' + end
                    db.session.commit()
                files[i].save(path + '\\' + str(i) + '.' + end)
            return redirect('/lka')
        return render_template('new_product.html', form=form)


@app.route('/categories/<category>', methods=['GET', 'POST'])
def category_product(category):
    products = ProductModel.query.filter_by(category=category).all()
    if request.method == 'POST':
        if request.form.get('cost_sort', None) == 'cost_sort':
            products = sorted(products, key=lambda s: int(s.cost))
        elif request.form.get('cost_sort_inv', None) == 'cost_sort_inv':
            products = sorted(products, key=lambda s: -int(s.cost))
        elif request.form.get('ask', False):
            return redirect('/all/' + request.form['ask'])
    return render_template('category_product.html', products=products[:100])

@app.route('/all/<ask>', methods=['POST', 'GET'])
def all_categories_ask(ask):
    products = ProductModel.query.filter_by(product_name=ask).all()
    if request.method == 'POST':
        if request.form.get('cost_sort', None) == 'cost_sort':
            products = sorted(products, key=lambda s: int(s.cost))
        if request.form.get('cost_sort_inv', None) == 'cost_sort_inv':
            products = sorted(products, key=lambda s: -int(s.cost))
        elif request.form.get('ask', False):
            return redirect('/all/' + request.form['ask'])
    return render_template('category_product.html', products=products[:100])


@app.route('/categories/<category>/<int:id>', methods=['POST', 'GET'])
def product_page(category, id):
    form = RedactionProductForm()
    product = ProductModel.query.filter_by(id=id).first()
    if request.method == 'GET':
        images = ['\\static\\image\\' + str(id) + '\\' + i
                  for i in os.listdir('static\\image\\' + str(id))]
        number = len(images)
        if 'user_id' in session and BasketModel.query.filter_by(
                product_id=id, user_id=session['user_id']).first():
            return render_template('product_page.html', product=product, images=images,
                                   number=number, in_basket=True, form=form)
        return render_template('product_page.html', product=product, images=images,
                               number=number, in_basket=False, form=form)
    elif request.method == 'POST':
        if request.form.get('submit_button', None) == 'append':
            if 'user_id' not in session:
                return redirect('/login')
            basket_product = BasketModel(product_id=id, user_id=session['user_id'])
            db.session.add(basket_product)
            db.session.commit()
            return redirect('/lka')

        elif request.form.get('submit_button', None) == 'pay':
            return redirect('/pay/' + str(id))
        elif form.validate_on_submit:
            if form.category.data:
                product.category = form.category.data
            if form.product_name.data:
                product.product_name = form.product_name.data
            if form.cost.data:
                product.cost = form.cost.data
            if form.count.data:
                product.count = form.count.data
            if form.s_description.data:
                product.s_description = form.s_description.data
            if form.b_description.data:
                product.b_description = form.b_description.data
            db.session.commit()
            path = os.path.join('static\\image\\', str(product.id))
            files = request.files.getlist("files")
            number = len(os.listdir(path))
            for i in range(len(files)):
                end = files[i].filename.split('.')[-1]
                if end not in ['jpg', 'jpeg', 'png', 'bmp', 'raw', 'gif', 'psd', 'tiff']:
                    form.submit.errors = ['Неверный формат изображения']
                    return '''Неверный формат изображения'''
                files[i].save(path + '\\' + str(number + i) + '.' + end)
            return redirect('/categories/' + category + '/' + str(id))



@app.route('/pay/<int:product_id>')
def pay(product_id):
    try:

        product = ProductModel.query.filter_by(id=product_id).first()
        if product.count == '0':
            return '''Товара нет на складе'''
        product.count = str(int(product.count) - 1)
        basket_product = BasketModel.query.filter_by(product_id=product_id,
                                                      user_id=session['user_id']).first()
        order_product = OrderModel(user_id=session['user_id'], product_id=product_id)
        db.session.add(order_product)
        db.session.delete(basket_product)
        db.session.commit()
        return redirect('/lka')
    except Exception as e:
        return e

'''
product = BasketModel.query.filter_by(product_id=3).first()
db.session.delete(product)
db.session.commit()'''



if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')

