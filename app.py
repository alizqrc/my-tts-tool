from flask import Flask, request, render_template_string, send_file
import os
from TTS.api import TTS

app = Flask(__name__)
tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")

HTML = """
<!doctype html>
<title>TTS</title>
<h1>Text to speech:</h1>
<form method="post">
  <textarea name="text" rows="4" cols="50"></textarea><br>
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

@app.route("/", methods=["GET", "POST"])
def index():
    audio_file = None
    if request.method == "POST":
        text = request.form["text"]
        if text.strip():
            audio_path = "output.wav"
            tts.tts_to_file(text=text, file_path=audio_path)
            audio_file = "/audio"  # route to serve the audio
    return render_template_string(HTML, audio_file=audio_file)

@app.route("/audio")
def serve_audio():
    return send_file("output.wav", mimetype="audio/wav")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
