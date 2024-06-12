from modules.local_imports import *
import os

class ResourceGenerator:
    def __init__(self, trend_number, text_articles=8, text_length=7, desc_articles=5, desc_length=3, language="English"):
        self.trend_number = trend_number
        self.text_articles = text_articles
        self.text_length = text_length
        self.desc_articles = desc_articles
        self.desc_length = desc_length
        self.language = language

    def generate_resources(self):
        trends = modules.scraping_and_summarization.get_trends()
        trend = trends[self.trend_number]
        text_script, tags = modules.scraping_and_summarization.apply_summarize_article_on_trend(trend, self.text_articles, self.text_length)
        description, _ = modules.scraping_and_summarization.apply_summarize_article_on_trend(trend, self.desc_articles, self.desc_length)
        images = modules.media_finder.searchAndDownloadImage(trend, text_script)
        
        if not images or not text_script:
            return None

        part = str(images[0].split("/"))[:-1].split("\\")
        path = os.path.join("media", part[2])
        tags = [f"#{tag}" for index, tag in enumerate(tags) if index < 15]
        tags = " ".join(tags)
        music_path = modules.media_finder.selectMusicByEmotion(modules.sentiment_analysis.get_summarization_emotion(text_script))
        audio_file = modules.text_to_speech.get_text_to_speech(text_script, path, self.language)
        srt_file = modules.subtitles.generate_srt(audio_file, path)
        
        output = {
            "Trend": trend, 
            "TextScript": text_script, 
            "Audio": audio_file,
            "subs": srt_file,
            "Description": description,
            "Tags": tags,
            "Images": images,
            "MusicPath": music_path
        }
        return output

    def main(self):
        output = self.generate_resources()
        if output:
            modules.editing.create_video_with_data(output)
            return output

# Utilizzo della classe ResourceGenerator
generator = ResourceGenerator(1, 10, 10)
output = generator.main()
