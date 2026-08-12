from flask import Flask, request, send_file
from flask_cors import CORS
import pyttsx3
from pydub import AudioSegment
from pydub.generators import Sine

app = Flask(__name__)
CORS(app)

@app.route('/generate', methods=['POST'])
def generate_song():
    data = request.get_json()
    text = data.get('text', '')

    # Voice banao
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.save_to_file(text, 'voice.wav')
    engine.runAndWait()

    # Background music banao
    background = Sine(440).to_audio_segment(duration=8000).apply_gain(-20)

    # Mix karo
    voice = AudioSegment.from_wav('voice.wav')
    final_song = background.overlay(voice)
    final_song.export('edusong_output.wav', format='wav')

    return send_file('edusong_output.wav', mimetype='audio/wav')

if __name__ == '__main__':
    app.run(debug=True, port=5000)