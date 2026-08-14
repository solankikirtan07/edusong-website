from flask import Flask, request, send_file
from flask_cors import CORS
from gtts import gTTS
from pydub import AudioSegment
from pydub.generators import Sine

app = Flask(__name__)
CORS(app)

@app.route('/generate', methods=['POST'])
def generate_song():
    data = request.get_json()
    text = data.get('text', '')

    # Voice banao (Google TTS)
    tts = gTTS(text=text, lang='en')
    tts.save('voice.mp3')

    # Background music banao
    background = Sine(440).to_audio_segment(duration=8000).apply_gain(-20)

    # Voice ko mix karo
    voice = AudioSegment.from_mp3('voice.mp3')
    final_song = background.overlay(voice)
    final_song.export('edusong_output.wav', format='wav')

    return send_file('edusong_output.wav', mimetype='audio/wav')

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)