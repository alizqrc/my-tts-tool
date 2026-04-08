from flask import Flask, request, render_template_string, send_file
from TTS.api import TTS
from pydub import AudioSegment
import imageio_ffmpeg as ffmpeg
import os
import uuid

# Ensure pydub can find ffmpeg
AudioSegment.converter = ffmpeg.get_ffmpeg_exe()

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

def tts_long_text(text, out_path="output.wav", chunk_size=200):
    """
    Splits text into chunks to avoid Tacotron2 RuntimeErrors.
    Returns a single combined audio file.
    """
    text_chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    combined = None

    for i, chunk in enumerate(text_chunks):
        temp_file = f"temp_{uuid.uuid4()}.wav"
        tts.tts_to_file(text=chunk, file_path=temp_file)
        segment = AudioSegment.from_wav(temp_file)
        if combined:
            combined += segment
        else:
            combined = segment
        os.remove(temp_file)

    combined.export(out_path, format="wav")

@app.route("/", methods=["GET", "POST"])
def index():
    audio_file = None
    if request.method == "POST":
        text = request.form["text"]
        if text.strip():
            audio_path = "output.wav"
            tts_long_text(text, out_path=audio_path)
            audio_file = "/audio"
    return render_template_string(HTML, audio_file=audio_file)

@app.route("/audio")
def serve_audio():
    return send_file("output.wav", mimetype="audio/wav")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
