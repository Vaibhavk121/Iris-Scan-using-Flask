from flask import Flask, request, render_template, redirect, url_for, flash
import os
import cv2
import numpy as np
import sqlite3

app = Flask(__name__)
app.secret_key = "secure_key"
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Database setup
DATABASE = 'eye_data.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (id INTEGER PRIMARY KEY, name TEXT, iris_data BLOB)''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Process the image
        iris_data = process_image(filepath)
        if iris_data is not None:
            flash("Iris successfully scanned!")
            return render_template('result.html', iris_data=str(iris_data))
        else:
            flash("Iris scan failed. Please try again.")
            return redirect(url_for('index'))

def process_image(image_path):
    """Process the image to extract iris pattern (stub example)"""
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    # Perform eye detection (placeholder)
    # Load Haarcascade for eye detection
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
    eyes = eye_cascade.detectMultiScale(img, scaleFactor=1.1, minNeighbors=5)

    if len(eyes) == 0:
        return None

    # Assume we're processing the first detected eye
    (x, y, w, h) = eyes[0]
    eye_region = img[y:y+h, x:x+w]

    # Placeholder: Converting eye region into a feature array
    iris_data = cv2.resize(eye_region, (50, 50)).flatten()
    return iris_data

@app.route('/register', methods=['POST'])
def register_user():
    name = request.form['name']
    iris_data = request.form['iris_data']
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, iris_data) VALUES (?, ?)", (name, iris_data))
    conn.commit()
    conn.close()
    flash("User registered successfully!")
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
