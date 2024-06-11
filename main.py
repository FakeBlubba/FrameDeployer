import scraping_and_summarization
import media_finder
import sentiment_analysis
import text_to_speech
import subtitles
import os
import editing 

def generate_resources(trend_number, text_articles = 8, text_length = 7, desc_articles = 5, desc_length = 3, language = "English"):
    language = "English"
    trends = scraping_and_summarization.get_trends()
    trend = trends[trend_number]
    text_script, tags = scraping_and_summarization.apply_summarize_article_on_trend(trend, text_articles, text_length)
    description, _ = scraping_and_summarization.apply_summarize_article_on_trend(trend, desc_articles, desc_length)
    images = []
    images = media_finder.searchAndDownloadImage(trend, text_script)
    if images == [] or not text_script or images == None:
        return
    part = str(images[0].split("/"))[:-1].split("\\")
    path = os.path.join("media", part[2])
    tags = [f"#{tag}" for index, tag in enumerate(tags) if index < 15]
    tags = " ".join(tags)
    music_path = ""
    music_path = media_finder.selectMusicByEmotion(sentiment_analysis.get_summarization_emotion(text_script))


    audio_file = text_to_speech.get_text_to_speech(text_script, path, language)
    srt_file = subtitles.generate_srt(audio_file, path)
    output =  {
        "Trend": trend, 
        "TextScript": text_script, 
        "Audio": audio_file,
        "subs": srt_file,
        "Description": description,
        "Tags": tags,
        "Images": images,
        "MusicPath": music_path
        }
    editing.create_video_with_data(output)
    
def main():
    output = generate_resources(1, 10, 10)
    if output != None:
        editing.create_video_with_data(output)
        return output
main()
