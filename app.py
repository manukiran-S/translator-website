from flask import Flask, render_template, request, redirect, url_for
import cv2
from PIL import Image
import pytesseract
from googletrans import Translator
from gtts import gTTS
import os
import speech_recognition as sr
import time
import scanQRcodeUtils
from time import sleep
import webbrowser
import ocrUtils


app = Flask(__name__)
translator = Translator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/image_to_text', methods=['GET', 'POST'])
def image_to_text():
    if request.method == 'POST':
        language = request.form['language']
        
        # Capture image from webcam
        cam = cv2.VideoCapture(0)
        ret, frame = cam.read()
        cam.release()
        
        if ret:

            text, frame = ocrUtils.readCharacters(frame)

            print(text)
            cv2.imshow("Output", frame)
            cv2.waitKey(1)
            # Perform OCR on captured image
            text = pytesseract.image_to_string(frame)
            
            # Translate text to the selected language
            translated_text = translator.translate(text, dest=language).text
            
            # Convert translated text to speech
            speech = gTTS(text=translated_text, lang=language, slow=False)
            speech.save('static/speech.mp3')
            
            return render_template('image_to_text.html', text=text, translated_text=translated_text, speech='static/speech.mp3')
    
    return render_template('image_to_text.html')


@app.route('/text_to_speech', methods=['GET', 'POST'])
def text_to_speech():
    if request.method == 'POST':
        text = request.form['text']
        language = request.form['language']
        
        # Translate the text to the specified language
        translator = Translator()
        try:
            translated_text = translator.translate(text, dest=language).text
        except AttributeError:
            translated_text = "Translation failed. Please try again later."
        
        # Convert translated text to speech
        speech = gTTS(text=translated_text, lang=language, slow=False)
        speech.save('static/speech.mp3')
        return render_template('text_to_speech.html', speech='static/speech.mp3')
    
    return render_template('text_to_speech.html')



@app.route('/voice_to_text', methods=['GET', 'POST'])
def voice_to_text():
    if request.method == 'POST':
        language = request.form['language']
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
        text = recognizer.recognize_google(audio)
        render_template('voice_to_text.html',text)
        translated_text = translator.translate(text, dest=language).text
        return render_template('voice_to_text.html', text=text, translated_text=translated_text)
    return render_template('voice_to_text.html')

@app.route('/text_to_text', methods=['GET', 'POST'])
def text_to_text():
    if request.method == 'POST':
        text = request.form['text']
        language = request.form['language']
        print(text)
        print(language)
        translated_text = translator.translate(text, dest=language)
        print("Translated text:", translated_text.text)
        return render_template('text_to_text.html', translated_text = translated_text.text)
    return render_template('text_to_text.html')

@app.route('/qr_scanner', methods=['GET', 'POST'])
def qr_scanner():
    if request.method == 'POST':
        cam = cv2.VideoCapture(0)
        #cam.resolution = (640, 480)
        time.sleep(2.0)
        
        while True:
            cap, img = cam.read()
            if img is None:
                print("Failed to capture image from camera")
                break
            
            qrDataList, img = scanQRcodeUtils.scanQRCodes(img)
    
            print(qrDataList)
        
        # Open the URL if any QR code data is detected
            for qrData in qrDataList:
                if qrData.startswith('http'):
                    webbrowser.open(qrData)
                    #return render_template('qr_scanner.html', webbrowser.open(qrData))
                
        
            cv2.imshow("Output", img)
            cv2.waitKey(1)
           
        cv2.destroyAllWindows()
        cam.release()
        return render_template('qr_scanner.html', webbrowser.open(qrData))
    return render_template('qr_scanner.html')

@app.route('/voice_to_speech', methods=['GET', 'POST'])
def voice_to_speech():
    if request.method == 'POST':
        language = request.form['language']
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            audio = recognizer.listen(source)
        text = recognizer.recognize_google(audio)
        speech = gTTS(text=text, lang=language, slow=False)
        speech.save('static/speech.mp3')
        return render_template('voice_to_speech.html', speech='static/speech.mp3')
    return render_template('voice_to_speech.html')

if __name__ == '__main__':
    app.run(debug=True)

