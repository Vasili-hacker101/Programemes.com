
from flask import Flask, url_for

app = Flask(__name__)


@app.route('/')
@app.route('/index')
def index():
    return "<h1>Привет, Яндекс! Я - Василий<h1>"


@app.route('/image_sample')
def image():
    return f'''<h1>Фото:<h1> <img src="{url_for('static', filename='img/sample_image.jpeg')}" alt="картинки нет">'''
    #return f'''<h1>Фото:<h1> <img src="static/img/sample_image.jpeg" alt="картинки нет">'''


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')


