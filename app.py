
import os
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from PIL import Image
import pytesseract
from pdf2image import convert_from_path, convert_from_bytes

UPLOAD_FOLDER = 'uploads'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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
                text += pytesseract.image_to_string(image)
        else:
            image = Image.open(filepath)
            text = pytesseract.image_to_string(image)

        return {'text': text}

@app.route('/download', methods=['POST'])
def download():
    content = request.form['content']
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'output.txt')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
