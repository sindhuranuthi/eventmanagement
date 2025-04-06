from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'secretkey'

# Initialize DB
def init_db():
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            date TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Admin credentials (hardcoded for demo)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

# Routes
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        if uname == ADMIN_USERNAME and pwd == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('admin'):
        return redirect(url_for('login'))
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    c.execute('SELECT * FROM events ORDER BY date')
    events = c.fetchall()
    conn.close()
    return render_template('dashboard.html', events=events)

@app.route('/add', methods=['GET', 'POST'])
def add_event():
    if not session.get('admin'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        date = request.form['date']
        conn = sqlite3.connect('events.db')
        c = conn.cursor()
        c.execute('INSERT INTO events (title, description, date) VALUES (?, ?, ?)', (title, description, date))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    return render_template('add_event.html')

@app.route('/delete/<int:event_id>')
def delete_event(event_id):
    if not session.get('admin'):
        return redirect(url_for('login'))
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    c.execute('DELETE FROM events WHERE id = ?', (event_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('login'))

@app.route('/register')
def register():
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    c.execute('SELECT * FROM events ORDER BY date')
    events = c.fetchall()
    conn.close()
    return render_template('register.html', events=events)

if __name__ == '__main__':
    app.run(debug=True)
