from flask import Flask, request, send_file
from flask_cors import CORS
from gtts import gTTS
from pydub import AudioSegment
from pydub.generators import Sine
import os
import requests

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"


def generate_lyrics(concept_text):
    """Gemini AI se concept ko rhyming song lyrics mein convert karo."""
    if not GEMINI_API_KEY:
        return concept_text  # agar key na ho, seedha original text use karo

    prompt = (
        "Turn the following study/answer text into short, simple, rhyming song "
        "lyrics (max 8 lines) that a student can sing to remember the concept. "
        "Keep it catchy, easy, and clear. Only output the lyrics, nothing else.\n\n"
        f"Text: {concept_text}"
    )

    try:
        response = requests.post(
            GEMINI_URL,
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=30
        )
        result = response.json()
        lyrics = result["candidates"][0]["content"]["parts"][0]["text"]
        return lyrics.strip()
    except Exception as e:
        print("Gemini error:", e)
        return concept_text  # fallback agar AI fail ho jaye


def detect_mood(text):
    """Simple keyword-based mood detection."""
    text_lower = text.lower()
    sad_words = ["sad", "loss", "death", "war", "difficult", "problem", "crisis"]
    happy_words = ["happy", "joy", "success", "growth", "energy", "celebrate"]

    if any(word in text_lower for word in sad_words):
        return "calm"
    elif any(word in text_lower for word in happy_words):
        return "upbeat"
    return "neutral"


def create_fallback_melody(duration_ms, mood="neutral"):
    note_sets = {
        "calm": [261, 293, 329, 293],
        "upbeat": [392, 440, 494, 440],
        "neutral": [261, 293, 329, 349, 392, 349]
    }
    notes = note_sets.get(mood, note_sets["neutral"])
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

    # Step 1: Concept ko lyrics mein badlo (Gemini AI)
    lyrics = generate_lyrics(text)

    # Step 2: Lyrics ko awaaz mein bolo
    tts = gTTS(text=lyrics, lang='en', slow=False)
    tts.save('voice.mp3')
    voice = AudioSegment.from_mp3('voice.mp3')

    # Step 3: Mood detect karke sahi background music choose karo
    mood = detect_mood(text)
    if os.path.exists('background.mp3'):
        music = AudioSegment.from_mp3('background.mp3')
    else:
        music = create_fallback_melody(len(voice), mood)

    # Step 4: Music ko voice ki length tak loop karo
    background = AudioSegment.silent(duration=0)
    while len(background) < len(voice) + 1500:
        background += music
    background = background[:len(voice) + 1500]

    background = background.apply_gain(-14)
    voice = voice.apply_gain(+2)

    final_song = background.overlay(voice, position=500)
    final_song = final_song.fade_in(500).fade_out(1000)

    final_song.export('edusong_output.mp3', format='mp3')

    return send_file('edusong_output.mp3', mimetype='audio/mpeg')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
