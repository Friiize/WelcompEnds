import json
import sys

import cv2
import numpy
import numpy as np
import os
import pytesseract
from flask import Flask, request, jsonify, redirect, url_for, flash, session

from flask_restful import Api, Resource
from flask_cors import CORS, cross_origin
from werkzeug.debug.repr import dump
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "C:/Users/Frize/current_project/WelcompEnds/ressource"
ALLOWED_EXTENSIONS = {'jpeg', 'png', 'jpg', 'pdf'}

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config.update(SECRET_KEY=os.urandom(24))
api = CORS(app)
pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'


class DataHandler(Resource):
    blocks = []

    def postprocess_image(self):
        image = 'C:/Users/Frize/current_project/WelcompEnds/ressource/factureImage.png'
        img = cv2.imread(image)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
        rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))
        dilation = cv2.dilate(thresh1, rect_kernel, 1)
        contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        img2 = img.copy()
        count = 0
        for cnt in contours:
            item = {"id": count, "content": None}
            x, y, w, h = cv2.boundingRect(cnt)
            rect = cv2.rectangle(img2, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cropped = rect[y:y + h, x:x + w]
            item["content"] = pytesseract.image_to_string(cropped, lang='fra')
            self.blocks.append(item)
            count = count + 1
        json_data = json.dumps(self.blocks)
        os.remove(image)
        return json_data


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def get_data():
    data_handler = DataHandler()
    request.files.get('image').save(os.path.join(app.config['UPLOAD_FOLDER'], request.files.get('image').filename))
    os.renames('C:/Users/Frize/current_project/WelcompEnds/ressource/factureImage', 'C:/Users/Frize/current_project/WelcompEnds/ressource/factureImage.png')
    return data_handler.postprocess_image()


if __name__ == '__main__':
    app.run(debug=True)
