import os
from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
from PIL import Image
import requests
from io import BytesIO

# Load the API key from environment variable
OCR_API_KEY = os.getenv("OCR_API_KEY")

UPLOAD_FOLDER = 'uploads'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def ocr_space_request(image_bytes):
    """Send image bytes to OCR.space API and return the parsed text."""
    response = requests.post(
        'https://api.ocr.space/parse/image',
        files={"filename": image_bytes},
        data={"apikey": OCR_API_KEY, "language": "eng"},
    )
    result = response.json()

    if result.get("IsErroredOnProcessing"):
        return "Error: " + result.get("ErrorMessage", ["Unknown error"])[0]

    return result["ParsedResults"][0]["ParsedText"]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    uploaded_file = request.files['file']
    if uploaded_file:
        filename = secure_filename(uploaded_file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        uploaded_file.save(filepath)

        text = ''
        if filename.lower().endswith('.pdf'):
            images = convert_from_path(filepath)
            for image in images:
                image_bytes = BytesIO()
                image.save(image_bytes, format='JPEG')
                image_bytes.seek(0)
                text += ocr_space_request(image_bytes)
        else:
            image = Image.open(filepath)
            image_bytes = BytesIO()
            image.save(image_bytes, format='JPEG')
            image_bytes.seek(0)
            text = ocr_space_request(image_bytes)

        return jsonify({'text': text})
    return jsonify({'error': 'No file uploaded'}), 400

@app.route('/download', methods=['POST'])
def download():
    content = request.form['content']
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'output.txt')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
