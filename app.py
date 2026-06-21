import os, json, io, datetime
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file

app = Flask(__name__)
app.secret_key = "kunci_rahasia_proyek_aman"
DATA_FILE = 'mahasiswa_data.json'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- FUNGSI DATABASE ---
def load_db():
    if not os.path.exists(DATA_FILE): return []
    try:
        with open(DATA_FILE, 'r') as f: return json.load(f)
    except: return []

def save_db(data):
    with open(DATA_FILE, 'w') as f: json.dump(data, f, indent=4)

# --- ROUTES ---
@app.route('/')
def home(): return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        db = load_db()
        user = next((item for item in db if item.get("nim") == request.form.get('nim')), None)
        if user:
            user['last_login'] = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
            save_db(db)
            session['user'] = user['nim']
            session['nama_lengkap'] = user.get('nama', 'User')
            return redirect(url_for('dashboard'))
        flash("NIM tidak ditemukan!")
    return render_template('login.html', title="Login")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        db = load_db()
        if any(item['nim'] == request.form.get('nim') for item in db):
            flash("NIM sudah terdaftar!")
            return redirect(url_for('signup'))
        db.append({
            'nim': request.form.get('nim'), 'nama': request.form.get('nama'),
            'jurusan': request.form.get('jurusan'), 'email': request.form.get('email'),
            'telp': request.form.get('telp'), 'password': '', 
            'last_login': 'Baru mendaftar'
        })
        save_db(db)
        return redirect(url_for('login'))
    return render_template('signup.html', title="Registrasi")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('dashboard.html', total_mahasiswa=len(load_db()), title="Dashboard Utama")

# --- CRUD MAHASISWA ---
@app.route('/mahasiswa')
def mahasiswa():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('mahasiswa.html', mahasiswa=load_db(), title="Data Mahasiswa")

@app.route('/tambah', methods=['GET', 'POST'])
def tambah():
    if 'user' not in session: return redirect(url_for('login'))
    if request.method == 'POST':
        db = load_db()
        db.append({'nim': request.form.get('nim'), 'nama': request.form.get('nama'), 
                   'jurusan': request.form.get('jurusan'), 'email': request.form.get('email'), 
                   'telp': request.form.get('telp'), 'password': '', 'last_login': 'N/A'})
        save_db(db)
        return redirect(url_for('mahasiswa'))
    return render_template('tambah.html', title="Tambah Mahasiswa")

@app.route('/lihat/<nim>')
def lihat(nim):
    if 'user' not in session: return redirect(url_for('login'))
    mhs = next((m for m in load_db() if m.get('nim') == nim), None)
    return render_template('tampilan.html', mhs=mhs, mode='view', title="Detail Mahasiswa")

@app.route('/edit/<nim>')
def edit(nim):
    if 'user' not in session: return redirect(url_for('login'))
    mhs = next((m for m in load_db() if m.get('nim') == nim), None)
    return render_template('tampilan.html', mhs=mhs, mode='edit', title="Edit Data Mahasiswa")

@app.route('/update/<nim>', methods=['POST'])
def update(nim):
    if 'user' not in session: return redirect(url_for('login'))
    db = load_db()
    mhs = next((m for m in db if m.get('nim') == nim), None)
    if mhs:
        mhs.update({'nama': request.form.get('nama'), 'jurusan': request.form.get('jurusan'), 
                    'email': request.form.get('email'), 'telp': request.form.get('telp')})
        save_db(db)
    return redirect(url_for('mahasiswa'))

@app.route('/hapus/<nim>')
def hapus(nim):
    if 'user' not in session: return redirect(url_for('login'))
    save_db([m for m in load_db() if m.get('nim') != nim])
    return redirect(url_for('mahasiswa'))

# --- LAPORAN & PENGATURAN ---
@app.route('/laporan')
def laporan():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('laporan.html', title="Laporan & Administrasi")

@app.route('/export_excel')
def export_excel():
    if 'user' not in session: return redirect(url_for('login'))
    df = pd.DataFrame(load_db())
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return send_file(output, download_name="Laporan_Mahasiswa.xlsx", as_attachment=True)

@app.route('/upload_surat', methods=['POST'])
def upload_surat():
    file = request.files.get('file')
    if file and file.filename != '':
        file.save(os.path.join(UPLOAD_FOLDER, file.filename))
        flash("File berhasil diupload!")
    return redirect(url_for('laporan'))

@app.route('/pengaturan')
def pengaturan():
    if 'user' not in session: return redirect(url_for('login'))
    db = load_db()
    mhs = next((m for m in db if m.get('nim') == session['user']), None)
    return render_template('pengaturan.html', mhs=mhs, title="Pengaturan")

@app.route('/update_settings', methods=['POST'])
def update_settings():
    if 'user' not in session: return redirect(url_for('login'))
    db = load_db()
    mhs = next((m for m in db if m.get('nim') == session['user']), None)
    if mhs:
        if request.form.get('password'):
            mhs['password'] = request.form.get('password')
        save_db(db)
        flash("Password berhasil diubah!")
    return redirect(url_for('pengaturan'))

if __name__ == '__main__': 
    app.run(debug=True)