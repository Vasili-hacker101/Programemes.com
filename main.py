from flask_wtf import FlaskForm
from flask import Flask, redirect, session, render_template, request, url_for
from wtforms import StringField, SubmitField, PasswordField, FileField, TextAreaField
from werkzeug.utils import secure_filename
from wtforms.validators import DataRequired
from werkzeug.datastructures import CombinedMultiDict
from db_2 import *
import os


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class AddNewsForm(FlaskForm):
    title = StringField('Заголовок мема', validators=[DataRequired()])
    content = TextAreaField('Текст мема')
    photo = FileField('Картинка')
    submit = SubmitField('Добавить')


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['UPLOAD_FOLDER'] = "users_data"
db = DB()
news = NewsModel(db.get_connection())
news = news.init_table()
users = UsersModel(db.get_connection())
users = users.init_table()

@app.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm()
    if form.validate_on_submit():
        user_name = form.username.data
        password = form.password.data
        user_model = UsersModel(db.get_connection())
        user_model.init_table()
        user_model.insert("admin", "admin_password")
        exists = user_model.exists(user_name, password)
        if (exists[0]):
            session['username'] = user_name
            session['user_id'] = exists[1]
            if user_name == "admin" and password == "admin_password":
                return redirect("/admin")
            return redirect("/index")
    return render_template('login_on_server.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = LoginForm()
    if form.validate_on_submit():
        user_name = form.username.data
        password = form.password.data
        user_model = UsersModel(db.get_connection())
        user_model.init_table()
        user_model.insert(user_name, password)
        return redirect("/login")
    return render_template('register_on_server.html', form=form)


@app.route('/admin')
def admin():
    user_model = UsersModel(db.get_connection())
    news_model = NewsModel(db.get_connection())
    users = user_model.get_all()
    m = []
    for user in users:
        news = news_model.get_all(user[0])
        if user[1] != "admin":
            m.append((user[1], len(news)))

    return render_template('admin.html', users=m)


@app.route('/user_page', methods=['GET', 'POST'])
def user_page():
    if 'username' not in session:
        return redirect('/login')
    news = NewsModel(db.get_connection())
    news = news.get_all(session['user_id'])
    return render_template('user_page.html', username=session['username'],
                           news=news)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    news = NewsModel(db.get_connection())
    news = news.get_all()
    user_model = UsersModel(db.get_connection())
    users = user_model.get_all()
    users_dict = dict()
    for i in users:
        users_dict[i[0]] = i[1]

    return render_template('index.html', news=news, users=users_dict)


@app.route('/index/<string:title>', methods=['GET', 'POST'])
def index_search(title):
    news = NewsModel(db.get_connection())
    news = news.search("title", title)
    user_model = UsersModel(db.get_connection())
    users = user_model.get_all()
    users_dict = dict()
    for i in users:
        users_dict[i[0]] = i[1]

    return render_template('index.html', news=news, users=users_dict)


@app.route('/logout')
def logout():
    session.pop('username',0)
    session.pop('user_id',0)
    return redirect('/index')


@app.route('/add_news', methods=['GET', 'POST'])
def add_news():
    if 'username' not in session:
        return redirect('/login')
    form = AddNewsForm(CombinedMultiDict((request.files, request.form)))
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        f = form.photo.data
        has_image = False
        nm = NewsModel(db.get_connection())
        if f:
            has_image = True
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], f"{nm.get_all()[-1][0]}.jpg"))

        nm.insert(title, content, has_image, session['user_id'])

        return redirect("/user_page")
    return render_template('add_news.html',
                           form=form, username=session['username'])


@app.route('/top', methods=['GET'])
def show_top():
    news = NewsModel(db.get_connection())
    top = news.show_top()
    user_model = UsersModel(db.get_connection())
    users = user_model.get_all()
    users_dict = dict()
    for i in users:
        users_dict[i[0]] = i[1]
    return render_template('top.html', top=top, users=users_dict)


@app.route('/like_news/<int:news_id>', methods=['GET'])
def like_news(news_id):
    if 'username' not in session:
        return redirect('/login')
    nm = NewsModel(db.get_connection())
    likes = nm.get(news_id)[5]
    nm.redact(news_id, None, None, likes + 1)
    return redirect("/index")


@app.route('/dislike_news/<int:news_id>', methods=['GET'])
def dislike_news(news_id):
    if 'username' not in session:
        return redirect('/login')
    nm = NewsModel(db.get_connection())
    likes = nm.get(news_id)[5]
    nm.redact(news_id, None, None, likes - 1)
    return redirect("/index")


@app.route('/delete_news/<int:news_id>', methods=['GET'])
def delete_news(news_id):
    if 'username' not in session:
        return redirect('/login')
    nm = NewsModel(db.get_connection())
    nm.delete(news_id)
    return redirect("/index")


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')




