"""Synthesizes speech from the input string of text or ssml.
Make sure to be working in a virtual environment.

Note: ssml must be well-formed according to:
    https://www.w3.org/TR/speech-synthesis/
"""
# REIMPORT TO ENABLE SCRIPT

from google.cloud import texttospeech
from datetime import datetime

now = datetime.now()
timestamp = now.strftime('%Y_%m_%d_%H_%M_%S')
# Instantiates a client
client = texttospeech.TextToSpeechClient()

# Set the text input to be synthesized
synthesis_input = texttospeech.SynthesisInput(text="コンビニ帰りに異世界へ召喚されたひきこもり学生の菜月昴")

# Build the voice request, select the language code ("en-US") and the ssml
# voice gender ("neutral")
# noinspection PyTypeChecker
voice = texttospeech.VoiceSelectionParams(
    language_code="ja-JP", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL, name="ja-JP-Wavenet-B"
)

# Select the type of audio file you want returned
audio_config = texttospeech.AudioConfig(
    # Can be MP3 or LINEAR16 (wav). OPUS is natively supported in browsers. MP3 is @ 32 kbps
    audio_encoding=texttospeech.AudioEncoding.OGG_OPUS,
    speaking_rate=1.0,
    pitch=0.0,
    volume_gain_db=0.0,
    )

# Perform the text-to-speech request on the text input with the selected
# voice parameters and audio file type
response = client.synthesize_speech(
    input=synthesis_input, voice=voice, audio_config=audio_config
    )

# The response's audio_content is binary.
# wb indicates writing in BINARY MODE - NEEDED for NON TEXT FILES.

with open(f"C:\\Users\\prav9\\OneDrive\\Desktop\\Coding\\MTL\Rekai\\tts_outputs\\google_tts_api_output_{timestamp}.opus", "wb") as out:
    # Write the response to the output file.
    out.write(response.audio_content)
    print('Audio content written to file "output.mp3"')

# dir(texttospeech.VoiceSelectionParams.)
