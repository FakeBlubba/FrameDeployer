import pyttsx3
import os
def get_text_to_speech(text, path, speaker_name = "English"):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    for voice in voices:
        if speaker_name in voice.name:
            engine.setProperty('voice', voice.id)
            break
    engine.setProperty('rate', 160)
    try:
        folder_path = os.path.join(path, "speech.wav")
        engine.save_to_file(text, folder_path)
        engine.runAndWait()
    except Exception as e:
        print(f"Errore durante il salvataggio del file audio: {e}")
    engine.stop()
    return folder_path



#speaker_name = "Microsoft Elsa Desktop - Italian (Italy)"  # per l'italiano
# speaker_name = "Microsoft Zira Desktop - English (United States)"  # per l'inglese
#get_text_to_speech("", text, "media\\Clippers08-02-2024", speaker_name = "English")
