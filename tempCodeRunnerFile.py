import os, json
from flask import Flask, render_template, request, redirect, url_for, flash, session, Response

app = Flask(__name__)
app.secret_key = "kunci_rahasia_proyek_aman"
DATA_FILE = 'mahasiswa_data.json'

def load_db():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            try: return json.load(f)
            except: return []
    return []

def save_db(data):
    with open(DATA_FILE, 'w') as f: json.dump(data, f, indent=4)

@app.route('/')
def index():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('index.html', mahasiswa=load_db())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        db = load_db()
        user = next((item for item in db if item.get("nim") == request.form['nim'] and item.get("password") == request.form['password']), None)
        if user:
            session['user'] = request.form['nim']
            return redirect(url_for('index'))
        flash("NIM atau Password salah!")
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        db = load_db()
        db.append({'nim': request.form['nim'], 'nama': request.form['nama'], 'password': request.form['password']})
        save_db(db)
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/add', methods=['POST'])
def add():
    db = load_db()
    db.append({
        'nim': request.form['nim'], 'nama': request.form['nama'],
        'jurusan': request.form['jurusan'], 'email': request.form['email'],
        'telp': request.form['telp'], 'password': '123'
    })
    save_db(db)
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)