import os
import requests
from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Read the API key from Render environment variable
OCR_SPACE_API_KEY = os.environ.get("OCR_SPACE_API_KEY")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ocr_space_file(filepath):
    with open(filepath, 'rb') as f:
        response = requests.post(
            'https://api.ocr.space/parse/image',
            files={'file': f},
            data={'apikey': OCR_SPACE_API_KEY, 'language': 'eng'},
        )
    try:
        result = response.json()
        if result.get('IsErroredOnProcessing'):
            error_msg = result.get('ErrorMessage', ['Unknown error'])[0]
            return {'error': f'OCR Error: {error_msg}'}
        return {'text': result['ParsedResults'][0]['ParsedText']}
    except Exception as e:
        return {'error': f'Failed to parse OCR response: {str(e)}'}


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    uploaded_file = request.files.get('file')
    if not uploaded_file or not allowed_file(uploaded_file.filename):
        return jsonify({'error': 'Invalid file type. Only JPG, JPEG, and PNG are allowed.'}), 400

    filename = secure_filename(uploaded_file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    uploaded_file.save(filepath)

    text = ocr_space_file(filepath)
    return jsonify({'text': text})

@app.route('/download', methods=['POST'])
def download():
    content = request.form['content']
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'output.txt')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
