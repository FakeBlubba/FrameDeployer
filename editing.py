import requests
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, TextClip, ColorClip
import requests
from tqdm import tqdm
import time

def transcribe_audio(audio_file_path):
    headers = {'authorization': "your_assemblyai_api_key"}
    response = requests.post('https://api.assemblyai.com/v2/upload', headers=headers, files={'file': open(audio_file_path, 'rb')})
    audio_url = response.json()['upload_url']

    json = {'audio_url': audio_url}
    transcription_response = requests.post('https://api.assemblyai.com/v2/transcript', json=json, headers=headers)
    transcript_id = transcription_response.json()['id']

    # Definisci il numero massimo di tentativi e l'intervallo di attesa
    max_attempts = 30
    attempts = 0

    with tqdm(total=max_attempts, desc="Trascrizione in corso") as pbar:
        while attempts < max_attempts:
            transcription_result = requests.get(f'https://api.assemblyai.com/v2/transcript/{transcript_id}', headers=headers)
            if transcription_result.json()['status'] == 'completed':
                pbar.update(max_attempts - attempts)  # Completa la barra di progresso
                return transcription_result.json()['words']
            elif transcription_result.json()['status'] == 'failed':
                print("Transcription failed")
                break
            else:
                time.sleep(10)  # Attendi prima del prossimo tentativo
                attempts += 1
                pbar.update(1)  # Aggiorna la barra di progresso per ogni tentativo

        if attempts == max_attempts:
            print("Raggiunto il numero massimo di tentativi senza completare la trascrizione.")


def generate_video_with_captions(words_with_timestamps, audio_path, output_path, words_per_caption=5):
    audio_clip = AudioFileClip(audio_path)
    video_clip = ColorClip(size=(1920, 1080), color=(0,0,0), duration=audio_clip.duration)
    captions = []
    print(words_with_timestamps)
    for i in range(0, len(words_with_timestamps), words_per_caption):
        segment_words = words_with_timestamps[i:i+words_per_caption]
        start_time = segment_words[0]['start'] / 1000 
        end_time = segment_words[-1]['end'] / 1000
        text = ' '.join(word['text'] for word in segment_words)

        caption = (TextClip(text, fontsize=24, color='white', size=(720, 360))
                   .set_start(start_time)
                   .set_end(end_time)
                   .set_position('center'))
        captions.append(caption)

    final_video = CompositeVideoClip([video_clip] + captions).set_audio(audio_clip)
    final_video.write_videofile(output_path, fps=24)


# Esempio di utilizzo
audio_file_path = 'media\\Buddy Hield09-02-2024\\speech.wav'
words_with_timestamps = transcribe_audio( audio_file_path)


# Esempio di utilizzo
output_path = 'media\\Buddy Hield09-02-2024\\video.mp4'
generate_video_with_captions(words_with_timestamps, audio_file_path, output_path, words_per_caption=5)

