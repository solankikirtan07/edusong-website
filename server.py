from flask import Flask, request, send_file
from flask_cors import CORS
from gtts import gTTS
from pydub import AudioSegment
from pydub.generators import Sine

app = Flask(__name__)
CORS(app)

def create_melody():
    # Ek chhota chord progression banate hain (C - Am - F - G jaisa feel)
    notes = [261, 293, 329, 349, 392, 349, 329, 293]  # C D E F G F E D scale-ish notes
    melody = AudioSegment.silent(duration=0)
    for note in notes:
        tone = Sine(note).to_audio_segment(duration=1000).apply_gain(-18)
        # Thoda fade laga do taaki smooth lage
        tone = tone.fade_in(50).fade_out(100)
        melody += tone
    return melody

@app.route('/generate', methods=['POST'])
def generate_song():
    data = request.get_json()
    text = data.get('text', '')

    # Voice banao (Google TTS)
    tts = gTTS(text=text, lang='en')
    tts.save('voice.mp3')

    voice = AudioSegment.from_mp3('voice.mp3')

    # Melody banao, voice jitni lambi loop karo
    melody = create_melody()
    background = melody
    while len(background) < len(voice) + 1000:
        background += melody
    background = background[:len(voice) + 1000].apply_gain(-8)

    # Mix karo
    final_song = background.overlay(voice)
    final_song.export('edusong_output.wav', format='wav')

    return send_file('edusong_output.wav', mimetype='audio/wav')

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)