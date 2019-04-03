from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, BooleanField,\
    SelectField, IntegerField
from wtforms.validators import DataRequired, length, NumberRange
from flask import Flask, render_template, redirect, session
from flask import request
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.security import generate_password_hash, check_password_hash
import shutil

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pokazeev'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class UserModel(db.Model):
    # Класс, отвечающий за авторизацию
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(80), unique=False, nullable=False)


class ProductModel(db.Model):
    # Класс, отвечающий за товары
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), unique=False, nullable=False)
    category = db.Column(db.String(100), unique=False, nullable=False)
    cost = db.Column(db.String(10), unique=False, nullable=False)
    count = db.Column(db.String(10), unique=False, nullable=False)
    s_description = db.Column(db.String(500), unique=False, nullable=False)
    b_description = db.Column(db.String(5000), unique=False, nullable=False)
    main_photo = db.Column(db.String(100), unique=False, nullable=True)


class BasketModel(db.Model):
    # Класс, отвечающий за корзину
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, unique=False, nullable=False)
    user_id = db.Column(db.Integer, unique=False, nullable=False)


class OrderModel(db.Model):
    # Класс, отвечающий за заказы
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, unique=False, nullable=False)
    user_id = db.Column(db.Integer, unique=False, nullable=False)


class LoginForm(FlaskForm):
    # Форма авторизации
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class NewProductForm(FlaskForm):
    # Форма добавления товара
    category = SelectField('Categories', choices=[
        ('phones', 'Телефоны и аксессуары'), ('computers', 'Компьютеры и оргтехника'),
        ('electronics', 'Электроника'), ('appliances', 'Бытовая техника'), ('clothes', 'Одежда'),
        ('children', 'Все для детей'), ('clock', 'Бижутерия и часы'), ('bag', 'Сумки и обувь'),
        ('house', 'Для дома и сада'), ('car', 'Автотовары'), ('health', 'Красота и здоровье'),
        ('sport', 'Спорт и развлечение')])
    product_name = StringField('Название товара', validators=[DataRequired(), length(max=100)])
    cost = IntegerField('Цена', validators=[DataRequired(), NumberRange(0, 10**10)])
    count = IntegerField('Количество', validators=[DataRequired(), NumberRange(0, 10**10)])
    s_description = TextAreaField('Краткое описание', validators=[length(max=500)])
    b_description = TextAreaField('Полное описание', validators=[length(max=5000)])
    submit = SubmitField('Добавить')


class RedactionProductForm(FlaskForm):
    # Форма редактирования товара
    category = SelectField('Categories', choices=[
        ('phones', 'Телефоны и аксессуары'), ('computers', 'Компьютеры и оргтехника'),
        ('electronics', 'Электроника'), ('appliances', 'Бытовая техника'), ('clothes', 'Одежда'),
        ('children', 'Все для детей'), ('clock', 'Бижутерия и часы'), ('bag', 'Сумки и обувь'),
        ('house', 'Для дома и сада'), ('car', 'Автотовары'), ('health', 'Красота и здоровье'),
        ('sport', 'Спорт и развлечение')])
    product_name = StringField('Измененное название', validators=[length(max=50)])
    cost = StringField('Новая цена', validators=[length(max=10)])
    count = StringField('Новое количество', validators=[length(max=10)])
    s_description = TextAreaField('Новое краткое описание', validators=[length(max=500)])
    b_description = TextAreaField('Новое полное описание', validators=[length(max=5000)])
    delete = BooleanField('Удалить товар')
    submit = SubmitField('Добавить')

'''
def find_asked_name(name, ask):
    nameList = name.lover().split()
    askList = ask.lover().split()
    count = 0
    for i in nameList:
        for j in askList:
            if i == j:
                count += 1
    return count'''


db.create_all()


@app.route('/', methods=['GET', 'POST'])
@app.route('/categories', methods=['GET', 'POST'])
def main_page():
    if request.method == 'GET':
        return render_template('main_page.html')
    elif request.method == 'POST' and request.form.get('ask', False):
        # Переход на точный поиск
        return redirect('/all/' + request.form['ask'])


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_in():
    # Регистрация
    form = LoginForm()
    form.username.errors = []
    form.submit.label.text = 'Зарегистрироваться'
    if form.validate_on_submit():
        user_name = form.username.data
        password = form.password.data
        try:
            # Регистрация пользователя и добавление в сессию. В UserModel username уникален.
            # Если имя пользователя существует - исключение
            user1 = UserModel(username=user_name, password_hash=generate_password_hash(password))
            db.session.add(user1)
            db.session.commit()
            session['username'] = user1.username
            session['user_id'] = user1.id
            # При добавлении в сессию, пользователь перенаправляется в личный кабинет
            return redirect("/lka")
        except Exception:
            form.username.errors = ['Данный пользователь уже существует']
            return render_template('authorization.html', name='Регистрация', form=form)
    return render_template('authorization.html', name='Регистрация', form=form, )


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Авторизация
    form = LoginForm()
    if form.validate_on_submit():
        user_name = form.username.data
        password = form.password.data
        # Поиск пользователя с введенным именем. Т.к. имя - уникальное значение, будет найден 1 или 0 пользователей
        user = UserModel.query.filter_by(username=user_name).first()
        # Проверка существования пользователя и соответствия пароля
        if user and check_password_hash(user.password_hash, password):
            session['username'] = user.username
            session['user_id'] = user.id
            return redirect("/lka")
        form.password.errors = ['Неверный пользователь или пароль']
    return render_template('authorization.html', name='Авторизация', form=form)


@app.route('/logout')
def logout():
    # Выход
    session.pop('username',0)
    session.pop('user_id',0)
    return redirect('/login')


@app.route('/lka', methods=['POST', 'GET'])
def lka():
    # Личный кабинет
    if 'username' not in session:
        return redirect('/login')
    # Список всех товаров в корзине
    basket_products = [ProductModel.query.filter_by(id=i.product_id).first()
                       for i in BasketModel.query.filter_by(user_id=session['user_id']).all()]

    if request.method == 'POST':
        for i in basket_products:
            # При отображении товаров в корзине существует кнопка оплаты,
            # с именем и значением при нажатии == id товара корзины
            if request.form.get(str(i.id), None) == str(i.id):
                return redirect('/pay/' + str(i.id))
    # Список всех заказов
    order_products = [ProductModel.query.filter_by(id=i.product_id).first()
                      for i in OrderModel.query.filter_by(user_id=session['user_id']).all()]
    return render_template('lka.html', basket_products=basket_products, order_products=order_products)


@app.route('/lka/new_product', methods=['GET', 'POST'])
def new_product():
    # Добавление товара. Только для администратора (admin; qwerty)
    form = NewProductForm()
    if 'username' not in session or session['username'] != 'admin':
        return '''<h1>Доступ к странице закрыт</h1>'''
    else:
        if form.validate_on_submit():
            # Добавление товара в БД
            product = ProductModel(product_name=form.product_name.data, category=form.category.data,
                                   cost=form.cost.data, count=form.count.data,
                                   s_description=form.s_description.data,
                                   b_description=form.b_description.data)
            db.session.add(product)
            db.session.commit()
            path = os.path.join('static\\image\\', str(product.id))
            os.mkdir(path)
            files = request.files.getlist("files")
            # Добавление изображений. Если изображения не заданы, создается пустая папка
            # Номер папки соответствует id товара
            for i in range(len(files)):
                end = files[i].filename.split('.')[-1]
                if end not in ['jpg', 'jpeg', 'png', 'bmp', 'raw', 'gif', 'psd', 'tiff']:
                    form.submit.errors = ['Неверный формат изображения']
                    return render_template('new_product.html', form=form)
                if i == 0:
                    # Первое изображение отображается в категориях и на странице товара,
                    # остальные - только на странице товара
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
            # Сортировка по возрастанию цены
            products = sorted(products, key=lambda s: int(s.cost))
        if request.form.get('cost_sort_inv', None) == 'cost_sort_inv':
            # Сортировка по убыванию цены
            products = sorted(products, key=lambda s: -int(s.cost))
        if request.form.get('ask', False):
            # Точный поиск
            return redirect('/all/' + request.form['ask'])
    return render_template('category_product.html', products=products)


@app.route('/all/<ask>', methods=['POST', 'GET'])
def all_categories_ask(ask):
    # Поиск по точному названию
    products = ProductModel.query.filter_by(product_name=ask).all()
    if request.method == 'POST':
        if request.form.get('cost_sort', None) == 'cost_sort':
            # Сортировка по возрастанию цены
            products = sorted(products, key=lambda s: int(s.cost))
        if request.form.get('cost_sort_inv', None) == 'cost_sort_inv':
            # Сортировка по убыванию цены
            products = sorted(products, key=lambda s: -int(s.cost))
        if request.form.get('ask', False):
            # Поиск по следующему названию
            return redirect('/all/' + request.form['ask'])
    return render_template('category_product.html', products=products)


@app.route('/categories/<category>/<int:id>', methods=['POST', 'GET'])
def product_page(category, id):
    # Страница товара
    form = RedactionProductForm()
    product = ProductModel.query.filter_by(id=id).first()
    if not product:
        # Проверка существования продукта с заданным id
        return '''<h1 style="background-color: rgb(255, 140, 140)">Товар не найден</h1>'''
    # Проверка наличия товара в корзине
    in_basket = True if 'user_id' in session and BasketModel.query.filter_by(
            product_id=id, user_id=session['user_id']).first() else False
    # Список путей до изображений товара
    images = ['\\static\\image\\' + str(id) + '\\' + i
              for i in os.listdir('static\\image\\' + str(id))]
    number = len(images)
    if request.method == 'POST':
        if request.form.get('submit_button', None) == 'append':
            if 'user_id' not in session:
                return redirect('/login')
            # Добавление товара в корзину авторизованного пользователя
            basket_product = BasketModel(product_id=id, user_id=session['user_id'])
            db.session.add(basket_product)
            db.session.commit()
            in_basket = True

        elif request.form.get('submit_button', None) == 'pay':
            # Оплата товара, если он находится в корзине
            return redirect('/pay/' + str(id))

        elif request.form.get('submit_button', None) == 'delete':
            basket = BasketModel.query.filter_by(user_id=session['user_id'], product_id=id).first()
            db.session.delete(basket)
            db.session.commit()
            in_basket = False
        elif form.validate_on_submit() and form.validate():
            # Редактирование информации о товаре. Поля, которые не нужно изменять остаются пустыми
            if form.category.data:
                product.category = form.category.data
            if form.product_name.data:
                product.product_name = form.product_name.data
            if form.cost.data:
                if not form.cost.data.isdigit():
                    form.cost.errors = ['Неверный формат числа']
                product.cost = form.cost.data
            if form.count.data:
                if not form.count.data.isdigit():
                    form.count.errors = ['Неверный формат числа']
                product.count = form.count.data
            if form.s_description.data:
                product.s_description = form.s_description.data
            if form.b_description.data:
                product.b_description = form.b_description.data
            path = os.path.join('static\\image\\', str(product.id))
            files = request.files.getlist("files")
            number = len(os.listdir(path))
            for i in range(len(files)):
                end = files[i].filename.split('.')[-1]
                if end not in ['jpg', 'jpeg', 'png', 'bmp', 'raw', 'gif', 'psd', 'tiff']:
                    form.submit.errors = ['Неверный формат изображения']
                    return '''<h1 style="background-color: rgb(255, 140, 140)>
                    Неверный формат изображения<h1>'''
                files[i].save(path + '\\' + str(number + i) + '.' + end)
            if form.delete.data:
                # Удаление товара
                # Удаление товара из таблици товаров
                product_model = ProductModel.query.filter_by(id=id).first()
                db.session.delete(product_model)
                # Удаление товара из корзины всех пользователей
                for i in BasketModel.query.filter_by(product_id=id).all():
                    db.session.delete(i)
                # Удаление товара из заказов всех пользователей
                for i in OrderModel.query.filter_by(product_id=id).all():
                    db.session.delete(i)
                # Удаление папки с изображениями товара
                shutil.rmtree('static/image/' + str(id))
                db.session.commit()
                return redirect('/categories/' + category)
            db.session.commit()
    return render_template('product_page.html', product=product, images=images,
                           number=number, in_basket=in_basket, form=form)


@app.route('/pay/<int:product_id>')
def pay(product_id):
    try:
        # Оплата товара. Магическим образом для оплаты товара достаточно нажать на кнопку оплаты
        product = ProductModel.query.filter_by(id=product_id).first()
        # Проверка наличия товара на складе
        if product.count == '0':
            return '''Товара нет на складе'''
        # Уменьшение количества товара
        product.count = str(int(product.count) - 1)
        # Перенос товара из корзины в заказы
        basket_product = BasketModel.query.filter_by(product_id=product_id,
                                                     user_id=session['user_id']).first()
        order_product = OrderModel(user_id=session['user_id'], product_id=product_id)
        db.session.add(order_product)
        db.session.delete(basket_product)
        db.session.commit()

        return redirect('/lka')
    except Exception as e:
        return e


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
