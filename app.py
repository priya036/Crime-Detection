from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
import os
from werkzeug.utils import secure_filename
from utils.face_recognition import verify_faces
import config
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

app = Flask(__name__)
app.config.from_object(config)


uri = "mongodb+srv://priya:5799@criminaldata.jhclr9m.mongodb.net/?retryWrites=true&w=majority&appName=CriminalData"

client = MongoClient(uri, server_api=ServerApi('1'))
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
    
db = client[config.DB_NAME]
criminals = db.criminals

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        criminal_id = request.form['criminal_id']
        
        # Check if criminal ID already exists
        if criminals.find_one({'criminal_id': criminal_id}):
            flash('Criminal ID already present!', 'danger')
            return redirect(url_for('register_present'))
            # return redirect(url_for('register'))

        name = request.form['name']
        record = {
            'criminal_id': criminal_id,
            'name': name,
            'father_name': request.form['father_name'],
            'gender': request.form['gender'],
            'religion': request.form['religion'],
            'blood_group': request.form['blood_group'],
            'body_mark': request.form['body_mark'],
            'nationality': request.form['nationality'],
            'crime_done': request.form['crime_done'],
            'image_path': None
        }

        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '':
                filename = secure_filename(f"{criminal_id}_{name}.jpg")
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)
                record['image_path'] = filename
        criminals.insert_one(record)
        flash('Record registered successfully!', 'success')
        return redirect(url_for('register_success'))

    return render_template('register.html')

@app.route('/register_success')
def register_success():
    return render_template('register_success.html')

@app.route('/register_present')
def register_present():
    return render_template('register_present.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        if 'image' in request.files:
            print("came in")
            image = request.files['image']
            print(image)
            if image.filename != '':
                filename = secure_filename(image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)

                for record in criminals.find():
                    if record['image_path']:
                        if verify_faces(image_path, os.path.join(app.config['UPLOAD_FOLDER'], record['image_path'])):
                            print(record)
                            return render_template('search.html', record=record)
                        
                flash('No match found!', 'danger')
                return render_template('search.html', record=None)
    print("came put")
    return render_template('search.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use the PORT environment variable if available
    app.run(debug=True, host='0.0.0.0', port=port)
