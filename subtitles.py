from pydub import AudioSegment
from pydub.silence import split_on_silence
import os
import datetime
import assemblyai as aai
import nltk
import re


def format_timestamp(milliseconds):
    # Converti i millisecondi in ore, minuti, secondi, e millisecondi
    hours = milliseconds // (1000*60*60)
    milliseconds -= hours * (1000*60*60)
    minutes = milliseconds // (1000*60)
    milliseconds -= minutes * (1000*60)
    seconds = milliseconds // 1000
    milliseconds -= seconds * 1000
    
    # Formatta le ore, i minuti, i secondi, e i millisecondi in una stringa SRT
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

def split_chunks(chunk_data, break_point=3):
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


#   ["testo", duration]
def process_chunk_data(chunk_data):
    chunk_data_processed = []    
    complete_duration = 0
    for index, chunk in enumerate(chunk_data):
        start_time = complete_duration
        complete_duration += chunk[1]
        end_time = complete_duration
        chunk_data_processed.append([chunk[0], format_timestamp(start_time), format_timestamp(end_time)])
    return chunk_data_processed
        
#   ["testo", start, end]
def write_srt(path, processed_chunk_data):
    with open(path, "w") as subtitle_file:
        for index, chunk in enumerate(processed_chunk_data):
            subtitle_file.write(f"{index + 1}\n{chunk[1]} --> {chunk[2]}\n{chunk[0]}\n\n")
    

def get_audio_info(path, chunk):
    transcriber = aai.Transcriber()
    text = transcriber.transcribe(path).text
    duration = len(chunk)
    return [text, duration]
    

def generate_chunks_and_get_data(audio_path, min_silence_len = 150, keep_silence = 150):
    sound = AudioSegment.from_file(audio_path)
    chunks = split_on_silence(sound, min_silence_len = min_silence_len, silence_thresh=sound.dBFS-14, keep_silence = keep_silence)
    chunk_data = []
    for i, chunk in enumerate(chunks):
        chunk_path = f"chunk{i}.wav"
        chunk.export(chunk_path, format="wav")
    
        chunk_data.append(get_audio_info(chunk_path, chunk))

    return chunk_data
        
def remove_chunks():
    for filename in os.listdir("."):
        if filename.startswith("chunk") and filename.endswith(".wav"):
            os.remove(filename)   
    
def generate_srt(audio_path, path, break_point = 3):
    aai.settings.api_key = "b59e382691cc47cca1e2e6b425569387"
    srt_path = os.path.join(path, "sub.srt")
    audio = get_audio_info(srt_path, srt_path)
    audio_file = audio[0]

    chunks_data = generate_chunks_and_get_data(audio_path)
    remove_chunks()

    #chunks_data = split_chunks(chunks_data, break_point)
    processed_chunk_data = process_chunk_data(chunks_data)
    

    write_srt(srt_path, processed_chunk_data)
    return srt_path


#path = "media/Apollo12-02-2024"
#generate_srt(path + "/speech.wav", path, 2)