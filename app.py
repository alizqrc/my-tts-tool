from flask import Flask, request, render_template_string, send_file
from TTS.api import TTS
from pydub import AudioSegment
import os

app = Flask(__name__)
tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")

HTML = """
<!doctype html>
<title>TTS</title>
<h1>Text to speech:</h1>
<form method="post">
  <textarea name="text" rows="6" cols="60"></textarea><br>
  <input type="submit" value="Speak">
</form>
{% if audio_file %}
  <h2>Listen:</h2>
  <audio controls autoplay>
    <source src="{{ audio_file }}" type="audio/wav">
    Your browser does not support the audio element.
  </audio>
{% endif %}
"""

def tts_long_text(text, out_path="output.wav", chunk_size=300):
    """Split long text into smaller chunks for TTS."""
    from tempfile import NamedTemporaryFile

    audio_segments = []
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    for chunk in chunks:
        with NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tts.tts_to_file(text=chunk, file_path=tmp.name)
            audio_segments.append(AudioSegment.from_wav(tmp.name))
            os.remove(tmp.name)
    combined = sum(audio_segments)
    combined.export(out_path, format="wav")

@app.route("/", methods=["GET", "POST"])
def index():
    audio_file = None
    if request.method == "POST":
        text = request.form.get("text", "").strip()
        if text:
            audio_path = "output.wav"
            tts_long_text(text, out_path=audio_path)
            audio_file = "/audio"
    return render_template_string(HTML, audio_file=audio_file)

@app.route("/audio")
def serve_audio():
    return send_file("output.wav", mimetype="audio/wav")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
