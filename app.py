from flask import Flask, request, render_template, redirect, url_for, send_from_directory
import os
import sqlite3
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DB_FILE = 'database.db'

# Initialize DB
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS upload_matrix (usn TEXT PRIMARY KEY)")
        conn.commit()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    usn = request.form.get('txt')
    date_str = request.form.get('date')
    image = request.files.get('image')

    if not (usn and date_str and image):
        return "Missing fields", 400

    date_col = date_str.replace('-', '_')
    filename = secure_filename(f"{usn}_{date_str}_{image.filename}")
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(filepath)

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        # Add column if not exists
        cursor.execute("PRAGMA table_info(upload_matrix)")
        columns = [col[1] for col in cursor.fetchall()]
        if date_col not in columns:
            cursor.execute(f"ALTER TABLE upload_matrix ADD COLUMN '{date_col}' TEXT")

        # Add row if not exists
        cursor.execute("SELECT usn FROM upload_matrix WHERE usn = ?", (usn,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO upload_matrix (usn) VALUES (?)", (usn,))

        # Update file path
        cursor.execute(f"UPDATE upload_matrix SET '{date_col}' = ? WHERE usn = ?", (filename, usn))
        conn.commit()

    return render_template('index.html', success=True, usn=usn)

@app.route('/display')
def display():
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM upload_matrix")
        data = cursor.fetchall()
        cursor.execute("PRAGMA table_info(upload_matrix)")
        columns = [col[1] for col in cursor.fetchall()]
    return render_template('display_matrix.html', data=data, columns=columns)

@app.route('/uploads/<path:filename>')
def send_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
        import os
        port = int(os.environ.get('PORT', 5000))  # Use Render's PORT environment variable
        app.run(host='0.0.0.0', port=port)

