import json
import cv2
import re
import os
import pytesseract
from flask import Flask, request
from flask_cors import CORS

UPLOAD_FOLDER = "C:/Users/Frize/current_project/WelcompEnds/ressource"
ALLOWED_EXTENSIONS = {'jpeg', 'png', 'jpg', 'pdf'}

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config.update(SECRET_KEY=os.urandom(24))
api = CORS(app)
pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'


def postprocess_image(image):
    # Init des variables
    item = {}
    text_item = {"text": []}
    date_item = {"deuDate": []}
    sold_item = {"sold": []}
    number_item = {"numbers": []}
    iban_item = {"iban": []}

    # Traitement de l'image pour le rendre plus lisible via OpenCV
    img = cv2.imread(image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))
    dilation = cv2.dilate(thresh1, rect_kernel, 1)
    contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    img2 = img.copy()

    for cnt in contours:
        # Création du contour de l'image avant de le traiter
        x, y, w, h = cv2.boundingRect(cnt)
        rect = cv2.rectangle(img2, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cropped = rect[y:y + h, x:x + w]

        # Traitement du contour en cours + remplacement de tout les \n par un espace
        temp = pytesseract.image_to_string(cropped, lang='fra')
        temp = temp.replace("\n", " ")

        # Regex d'une date format DD-MM ou MONTH-YYYY
        regex = re.findall(
            r'(\d{2}|\d{1})[\s|.|/|-](\d{2}|(?:[Jj]an(?:vier|.)?|[Ff]ev(?:rier|.)?|[Mm]ar(?:s|.)?|[Aa]vr(?:il|.)?|[Mm]ai|[Jj]ui(?:n|.)?|[Jj]ui(?:llet|.)?|[Aa]oû(?:t|.)?|[Ss]ep(?:tembre|.)?|[Oo]ct(?:obre|.)?|[Nn]ov(?:embre|.)?|[Dd]ec(?:embre|.)?))[\s|.|/|-]([1-9]\d{3})', # Regex qui fonctionne
            temp)
        if regex != None:
            for date in regex:
                date_item["deuDate"].append({"date": date})
        re.purge()

        # Regex du sold de la facture
        regex = re.findall(
            r'(([0-9|oO]{1}|[0-9|oO]{2})|[\s(\d|Oo{3}]*)(,|.)(\d{2}|[Oo]{2})[\s]{0,1}(€|EUR|EURO|e){1}', # Regex qui fonctionne
            temp)
        if regex != None:
            for sold in regex:
                sold_item["sold"].append({"sold": sold})
        re.purge()

        # Regex de l'IBAN
        regex = re.findall(
                r"([A-Z]{2}\s*)(\d{2}[\s*])([\d{4}\s*]+)",  # Regex qui fonctionne
                temp)
        if regex != None:
            for iban in regex:
                iban_item["iban"].append({"iban": iban})
        re.purge()

        # Regex des chiffres restant (Numéro de facture trop hazardeux pour bien l'identifié
        regex = re.findall(
                r'\d{4,}[\s|\D\d{4,}]{0,}[\s|\S]\d{0,}',
                temp)
        if regex != None:
            for number in regex:
                number_item["numbers"].append({"number": number})

        # Cache des contours de texte au cas où
        text_item["text"].append(temp)
        re.purge()

    # Ajout de tout les regex dans la list item
    item.update(sold_item)
    item.update(date_item)
    item.update(iban_item)
    item.update(number_item)
    item.update(text_item)

    # Transformation de la list en JSON et retour du JSON côté client
    json_data = json.dumps(item)
    return json_data


@app.route('/', methods=['GET', 'POST'])
def get_data():
    # Init des variables
    imported_file = os.path.join(app.config['UPLOAD_FOLDER'], request.files.get('image').filename)
    image = UPLOAD_FOLDER + '/factureImage.png'

    # Récupération et traitement du fichier
    request.files.get('image').save(imported_file)
    os.renames(imported_file, image)
    processed_data = postprocess_image(image)
    os.remove(image)
    return processed_data


if __name__ == '__main__':
    app.run(debug=True)