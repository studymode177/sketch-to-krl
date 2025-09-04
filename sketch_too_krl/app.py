from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import cv2
import numpy as np
from werkzeug.utils import secure_filename
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))
from utils.image_processor import SketchProcessor
from utils.krl_generator import KRLGenerator

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize modules
sketch_processor = SketchProcessor()
krl_generator = KRLGenerator()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        session['filepath'] = filepath
        session['filename'] = filename
        return redirect(url_for('process_sketch'))
    
    flash('Invalid file type. Please upload PNG or JPG images.')
    return redirect(url_for('index'))

@app.route('/process')
def process_sketch():
    filepath = session.get('filepath')
    if not filepath:
        flash('No file uploaded')
        return redirect(url_for('index'))
    
    try:
        # Process the sketch to extract paths
        processed_image_path, paths = sketch_processor.process_sketch(filepath)
        session['processed_image_path'] = processed_image_path
        session['paths'] = paths
        
        return render_template('process.html', 
                              filename=session.get('filename'),
                              processed_image=processed_image_path)
    except Exception as e:
        flash(f'Error processing sketch: {str(e)}')
        return redirect(url_for('index'))

@app.route('/generate', methods=['GET', 'POST'])
def generate_krl():
    if request.method == 'POST':
        # Get user choices from form
        start_position = request.form.get('start_position')
        motion_types = request.form.getlist('motion_types')
        interpretation = request.form.get('interpretation')
        clarifications = request.form.get('clarifications')
        
        # Store choices in session
        session['start_position'] = start_position
        session['motion_types'] = motion_types
        session['interpretation'] = interpretation
        session['clarifications'] = clarifications
        
        # Generate KRL code
        paths = session.get('paths', [])
        krl_code = krl_generator.generate_program(start_position, motion_types, interpretation, clarifications, paths)
        session['krl_code'] = krl_code
        
        return render_template('result.html', krl_code=krl_code)
    
    # For GET request, we need to determine how many paths we have to create appropriate form
    paths = session.get('paths', [])
    return render_template('generate.html', paths=paths)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)