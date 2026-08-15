from flask import Flask, request, send_file
from flask_cors import CORS
from gtts import gTTS
from pydub import AudioSegment
from pydub.generators import Sine
import os

app = Flask(__name__)
CORS(app)

def create_fallback_melody(duration_ms):
    """Agar background.mp3 file na mile, to ek pleasant melody generate karo (beep se better)."""
    notes = [261, 293, 329, 349, 392, 440, 392, 349]  # C D E F G A G F
    melody = AudioSegment.silent(duration=0)
    while len(melody) < duration_ms + 2000:
        for note in notes:
            tone = Sine(note).to_audio_segment(duration=600).apply_gain(-20)
            tone = tone.fade_in(30).fade_out(150)
            melody += tone
    return melody[:duration_ms + 2000]

@app.route('/generate', methods=['POST'])
def generate_song():
    data = request.get_json()
    text = data.get('text', '')

    if not text or not text.strip():
        return {"error": "Text is empty"}, 400

    # Step 1: Voice banao (Google TTS - natural sounding)
    tts = gTTS(text=text, lang='en', slow=False)
    tts.save('voice.mp3')
    voice = AudioSegment.from_mp3('voice.mp3')

    # Step 2: Background music - real file use karo agar available hai
    if os.path.exists('background.mp3'):
        music = AudioSegment.from_mp3('background.mp3')
    else:
        music = create_fallback_melody(len(voice))

    # Step 3: Music ko voice ki length tak loop karo
    background = AudioSegment.silent(duration=0)
    while len(background) < len(voice) + 1500:
        background += music
    background = background[:len(voice) + 1500]

    # Step 4: Volume balance - music halka, voice clear
    background = background.apply_gain(-14)
    voice = voice.apply_gain(+2)

    # Step 5: Voice ko thoda center mein start karo aur mix karo
    final_song = background.overlay(voice, position=500)

    # Step 6: Fade in/out for polish
    final_song = final_song.fade_in(500).fade_out(1000)

    final_song.export('edusong_output.mp3', format='mp3')

    return send_file('edusong_output.mp3', mimetype='audio/mpeg')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
