
import sqlite3


class DB:
    def __init__(self):
        conn = sqlite3.connect('news.db', check_same_thread=False)
        self.conn = conn

    def get_connection(self):
        return self.conn

    def __del__(self):
        self.conn.close()


class NewsModel:
    def __init__(self, connection):
        self.connection = connection

    def get_connection(self):
        return self.connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS news 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             title VARCHAR(100),
                             content VARCHAR(1000),
                             user_id INTEGER,
                             n_date TEXT,
                             likes INTEGER,
                             has_image BOOLEAN)''')
        cursor.close()
        self.connection.commit()

    def insert(self, title, content, has_image, user_id):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO news 
                          (title, content, user_id, n_date, likes, has_image) 
                          VALUES (?, ?, ?, DATETIME('now'), 0, ?)''', (title, content, str(user_id), has_image))
        cursor.close()
        self.connection.commit()

    def get(self, news_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM news WHERE id = ?", (str(news_id),))
        row = cursor.fetchone()
        return row

    def get_all(self, user_id=None):
        cursor = self.connection.cursor()
        if user_id:
            cursor.execute("SELECT * FROM news WHERE user_id = ? ORDER BY n_date desc, title",
                           (str(user_id),))
        else:
            cursor.execute("SELECT * FROM news ORDER BY n_date desc, title")
        rows = cursor.fetchall()
        return rows

    def show_top(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM news ORDER BY likes desc LIMIT 5")
        rows = cursor.fetchall()
        return rows

    def search(self, criterion, search):
        cursor = self.connection.cursor()
        if search != "":
            cursor.execute(f'SELECT * FROM news WHERE title LIKE ? ORDER BY n_date desc, title', ("%" + search + "%",))
        else:
            cursor.execute("SELECT * FROM news ORDER BY n_date desc, title")
        rows = cursor.fetchall()
        return rows

    def delete(self, news_id=None):
        cursor = self.connection.cursor()
        if news_id:
            cursor.execute('''DELETE FROM news WHERE id = ?''', (str(news_id),))
        else:
            cursor.execute('''DELETE FROM news''')
        cursor.close()
        self.connection.commit()

    def redact(self, news_id, title, content, likes):
        if not title:
            title = self.get(news_id)[1]

        if not content:
            content = self.get(news_id)[2]

        if not likes:
            likes = self.get(news_id)[5]
        cursor = self.connection.cursor()
        cursor.execute('''UPDATE news SET title = ?, content = ?, likes = ? WHERE id = ?''', (title, content, likes, news_id))
        cursor.close()
        self.connection.commit()


class UsersModel:
    def __init__(self, connection):
        self.connection = connection

    def get_connection(self):
        return self.connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             user_name VARCHAR(50),
                             password_hash VARCHAR(128)
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, user_name, password_hash):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO users 
                          (user_name, password_hash) 
                          VALUES (?,?)''', (user_name, password_hash))
        cursor.close()
        self.connection.commit()

    def get(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (str(user_id),))
        row = cursor.fetchone()
        return row

    def get_all(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        return rows

    def exists(self, user_name, password_hash):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE user_name = ? AND password_hash = ?",
                       (user_name, password_hash))
        row = cursor.fetchone()
        return (True, row[0]) if row else (False,)




