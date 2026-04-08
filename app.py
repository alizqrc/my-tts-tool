from flask import Flask, request, render_template_string, send_file
import os
import re
from TTS.api import TTS
from pydub import AudioSegment

app = Flask(__name__)

# Load model
tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")

HTML = """
<!doctype html>
<title>TTS</title>
<h1>Text to speech:</h1>

<form method="post">
  <textarea name="text" rows="8" cols="60"></textarea><br>
  <input type="submit" value="Speak">
</form>

{% if audio_file %}
  <h2>Listen:</h2>
  <audio controls autoplay>
    <source src="{{ audio_file }}" type="audio/wav">
  </audio>
{% endif %}
"""

# --- Split into sentences ---
def split_into_sentences(text):
    sentences = re.split(r'(?<=[.!?]) +', text)
    return [s.strip() for s in sentences if s.strip()]

# --- SAFE TTS (prevents crashes) ---
def safe_tts_to_file(text, file_path):
    text = text.strip()

    # Force minimum length
    if len(text) < 20:
        text = text + " ... continuing."

    try:
        tts.tts_to_file(text=text, file_path=file_path)
    except RuntimeError:
        print(f"Retrying failed chunk: {text}")

        # Retry with padding
        safe_text = text + " This is additional padding to stabilize the model."
        try:
            tts.tts_to_file(text=safe_text, file_path=file_path)
        except Exception:
            print("Skipping broken chunk.")

# --- NATURAL LONG TEXT HANDLER ---
def tts_natural(text, out_path="output.wav"):
    sentences = split_into_sentences(text)

    final_audio = AudioSegment.silent(duration=0)
    buffer = ""

    for i, sentence in enumerate(sentences):
        sentence = sentence.strip()

        # Skip useless tiny fragments
        if len(sentence) < 5:
            continue

        # Merge short sentences
        if len(sentence) < 40:
            buffer += " " + sentence
            continue

        if buffer:
            sentence = buffer + " " + sentence
            buffer = ""

        temp_file = f"temp_{i}.wav"

        safe_tts_to_file(sentence, temp_file)

        if os.path.exists(temp_file):
            seg = AudioSegment.from_wav(temp_file)

            # Add pause
            seg += AudioSegment.silent(duration=200)

            # Smooth transitions
            if len(final_audio) > 0:
                final_audio = final_audio.append(seg, crossfade=100)
            else:
                final_audio = seg

            os.remove(temp_file)

    # Handle leftover buffer
    if buffer.strip():
        temp_file = "temp_last.wav"
        safe_tts_to_file(buffer.strip(), temp_file)

        if os.path.exists(temp_file):
            seg = AudioSegment.from_wav(temp_file)
            final_audio += seg
            os.remove(temp_file)

    # Final fallback (prevents crash)
    if len(final_audio) == 0:
        tts.tts_to_file(text="Error processing text.", file_path=out_path)
    else:
        final_audio.export(out_path, format="wav")

# --- ROUTES ---
@app.route("/", methods=["GET", "POST"])
def index():
    audio_file = None

    if request.method == "POST":
        text = request.form.get("text", "").strip()

        if text:
            audio_path = "output.wav"
            tts_natural(text, out_path=audio_path)
            audio_file = "/audio"

    return render_template_string(HTML, audio_file=audio_file)

@app.route("/audio")
def serve_audio():
    return send_file("output.wav", mimetype="audio/wav")

# --- RUN ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
