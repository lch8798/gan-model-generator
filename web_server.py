import os
from flask import Flask, render_template, send_file

PORT = 13001

app = Flask(__name__)

IMAGE_DIR = 'datasets/image'
TEXT_DIR = 'datasets/text'

@app.route('/')
def index():
    images = [f for f in os.listdir(IMAGE_DIR) if f.endswith('.jpg') or f.endswith('.jpeg') or f.endswith('.png')]
    texts = [f for f in os.listdir(TEXT_DIR) if f.endswith('.txt')]
    data = []
    for image in images:
        text_path = os.path.join(TEXT_DIR, os.path.splitext(image)[0] + '.txt')
        with open(text_path, 'r') as f:
            text = f.read()
        data.append({ 'image': image, 'text': text })
    return render_template('index.html', data=data)

@app.route('/image/<path:filename>')
def image(filename):
    return send_file(os.path.join(IMAGE_DIR, filename))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)
