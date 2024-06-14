import shutil
from pydub import AudioSegment
from pydub.silence import split_on_silence
import os
import datetime
import nltk
import re

# Importing the API Key
from dotenv import load_dotenv
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

def split_chunks(chunk_data, break_point=3):
    """
    Splits audio chunks based on silence and filters out stopwords.

    Args:
    - chunk_data (list): List of chunks where each chunk is [transcription, duration].
    - break_point (int): Number of segments to split each chunk.

    Returns:
    - list: List of segmented chunks with reduced stopwords.
    """
    new_chunk_data = []
    for index, chunk in enumerate(chunk_data):
        transcription, duration = chunk
        new_chunks = []
        if transcription is None:
            continue

        words = nltk.word_tokenize(transcription)
        total_words = len(words)
        filtered_indices = [i for i, word in enumerate(words) if word.lower() not in nltk.corpus.stopwords.words('english')]

        if break_point + 2 <= len(filtered_indices):
            total_filtered_words = len(filtered_indices)
            words_per_segment = total_filtered_words // break_point
            remainder_words = total_filtered_words % break_point

            for i in range(0, total_filtered_words, words_per_segment + (1 if remainder_words > 0 else 0)):
                segment_end = i + words_per_segment + (1 if remainder_words > 0 else 0)
                if remainder_words > 0:
                    remainder_words -= 1
                segment_indices = filtered_indices[i:segment_end]

                if not segment_indices:
                    continue

                segment_start = segment_indices[0]
                segment_end = segment_indices[-1]
                segment_words = words[segment_start:segment_end + 1]

                segment_duration = duration * (len(segment_indices) / total_filtered_words)
                new_chunks.append([" ".join(segment_words), segment_duration])

        else:
            new_chunks.append(chunk)
        
        new_chunk_data.extend(new_chunks)

    return new_chunk_data


#   ["test", duration]
def process_chunk_data(chunk_data):
    """
    Apply text preprocessing on chunks.

    Args:
    - chunk_data (chunk): A chunk of audio.

    Returns:
    - list: List of segmented chunks with duration.
    """
    chunk_data_processed = []    
    complete_duration = 0
    for index, chunk in enumerate(chunk_data):
        start_time = complete_duration
        complete_duration += chunk[1]
        end_time = complete_duration
        chunk_data_processed.append([chunk[0], format_timestamp(start_time), format_timestamp(end_time)])
    return chunk_data_processed
        
#   ["test", start, end]
def write_srt(path, processed_chunk_data):
    """
    Writes SRT subtitle file based on processed chunk data.

    Args:
    - path (str): Path to write the SRT file.
    - processed_chunk_data (list): List of processed chunk data where each chunk is [transcription, start_time, end_time].
    """
    with open(path, "w") as subtitle_file:
        for index, chunk in enumerate(processed_chunk_data):
            subtitle_file.write(f"{index + 1}\n{chunk[1]} --> {chunk[2]}\n{chunk[0]}\n\n")
    

def get_audio_info(path, chunk):
    """
    Retrieves audio information using transcription API.

    Args:
    - path (str): Path to the audio file.
    - chunk (AudioSegment): Audio chunk for which to retrieve information.

    Returns:
    - list: List containing transcription text and duration.
    """
    transcriber = aai.Transcriber()
    text = transcriber.transcribe(path).text
    duration = len(chunk)
    return [text, duration]
    

def generate_chunks_and_get_data(audio_path, min_silence_len = 150, keep_silence = 150):
    """
    Generates audio chunks from the input audio file and retrieves data for each chunk.

    Args:
    - audio_path (str): Path to the input audio file.
    - min_silence_len (int): Minimum length of silence to split audio chunks (default: 150).
    - keep_silence (int): Amount of silence to keep at the beginning and end of chunks (default: 150).

    Returns:
    - list: List of audio chunk data where each chunk is [transcription, duration].
    """
    sound = AudioSegment.from_file(audio_path)
    chunks = split_on_silence(sound, min_silence_len = min_silence_len, silence_thresh=sound.dBFS-14, keep_silence = keep_silence)
    chunk_data = []
    chunk_folder = os.path.join(audio_path.replace(audio_path.split("\\")[-1], "") , "chunks")
    if not os.path.exists(chunk_folder):
        os.makedirs(chunk_folder)
    for i, chunk in enumerate(chunks):
        chunk_path = f"chunk{i}.wav"
        chunk_path = os.path.join(chunk_folder, f"chunk{i}.wav")
        chunk.export(chunk_path, format="wav")
    
        chunk_data.append(get_audio_info(chunk_path, chunk))

    return chunk_data
        
def remove_chunks(audio_path):
    """
    Removes the 'chunks' folder and all its contents.

    Args:
    - audio_path (str): Path to the input audio file.
    """
    chunk_folder = os.path.join(os.path.dirname(audio_path), "chunks")
    if os.path.exists(chunk_folder):
        shutil.rmtree(chunk_folder)  
    
def generate_srt(audio_path, path, break_point = 3):
    """
    Generates SRT subtitle file for the input audio file.

    Args:
    - audio_path (str): Path to the input audio file.
    - path (str): Directory path where the SRT file will be saved.
    - break_point (int): Number of segments to split each chunk.

    Returns:
    - str: Path to the generated SRT subtitle file.
    """
    srt_path = os.path.join(path, "sub.srt")
    audio = get_audio_info(audio_path, srt_path)
    audio_file = audio[0]

    chunks_data = generate_chunks_and_get_data(audio_path)
    remove_chunks(audio_path)

    #chunks_data = split_chunks(chunks_data, break_point)
    processed_chunk_data = process_chunk_data(chunks_data)
    

    write_srt(srt_path, processed_chunk_data)
    return srt_path


#path = ""
#generate_srt(path + "/speech.wav", path, 2)