from pydub import AudioSegment
from pydub.silence import split_on_silence
import os
from dotenv import load_dotenv

# Importing the API Key
load_dotenv(dotenv_path='data/var.env')
API_KEY = os.getenv("aai")
import assemblyai as aai
aai.settings.api_key = API_KEY


def format_timestamp(milliseconds):
    """
    Formats timestamp from milliseconds to HH:MM:SS,MMM format.

    Args:
    - milliseconds (int): Time duration in milliseconds.

    Returns:
    - str: Formatted timestamp string in HH:MM:SS,MMM format.
    """
    hours = milliseconds // (1000*60*60)
    milliseconds -= hours * (1000*60*60)
    minutes = milliseconds // (1000*60)
    milliseconds -= minutes * (1000*60)
    seconds = milliseconds // 1000
    milliseconds -= seconds * 1000
    
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

def generate_srt(audio_path, path, chars_limit = 22):
    
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_path)
    srt_path = os.path.join(path, "sub.srt")

    srt = transcript.export_subtitles_srt(chars_per_caption=chars_limit)


    with open(srt_path, "w") as f:
        f.write(srt)
    return srt_path

#path = ""
#generate_srt(path + "/speech.wav", path, 2)