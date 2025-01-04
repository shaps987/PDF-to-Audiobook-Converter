from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from werkzeug.utils import secure_filename
import os
import pyttsx3
from PyPDF2 import PdfReader

# Flask app setup
app = Flask(__name__)
app.secret_key = 'supersecretkey'  # For flash messages
UPLOAD_FOLDER = 'static/audio'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Helper function to check file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route for the home page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle file upload
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Convert PDF to audio
        audio_filename = convert_pdf_to_audio(filepath, filename)
        return render_template('result.html', audio_file=audio_filename)

    flash('Invalid file type. Please upload a PDF.')
    return redirect(url_for('index'))

# Route to download the audio file
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

# Function to convert PDF to audiobook
def convert_pdf_to_audio(pdf_path, filename):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()

    engine = pyttsx3.init()
    audio_filename = f"{filename.rsplit('.', 1)[0]}.mp3"
    audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_filename)

    # Convert text to speech and save
    engine.save_to_file(text, audio_path)
    engine.runAndWait()
    return audio_filename

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)