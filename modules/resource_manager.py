import os

import modules.web_scraper
import modules.editing
import modules.sentiment_analysis
import modules.subtitles
import modules.text_to_speech
import modules.summarize
import modules.media_finder

class ResourceManager:
    def __init__(self, trend_number, number_of_articles_to_read = 10, text_articles=8, text_length=7, desc_articles=5, desc_length=3, language="English"):
        self.trend_number = trend_number
        self.number_of_articles_to_read = number_of_articles_to_read
        self.text_articles = text_articles
        self.text_length = text_length
        self.desc_articles = desc_articles
        self.desc_length = desc_length
        self.language = language

    def generate_resources(self):
        trend = modules.web_scraper.get_trends()
        contents = modules.web_scraper.get_trend_contents(self.trend_number, self.number_of_articles_to_read)
        desc_contents_scrapped = modules.web_scraper.get_trend_contents(self.trend_number, self.desc_articles)
        if(not contents):
            print("Error during the searching for the selected trend.")
            return False
        
        text_script, tags = modules.summarize.apply_summarization_article_on_trend(contents, self.text_length)
        description, _ = modules.summarize.apply_summarization_article_on_trend(desc_contents_scrapped, self.desc_length)
        
        if(not text):
            print("Error during the summarization.")
            return False
        
        images = modules.media_finder.searchAndDownloadImage(trend[self.trend_number], text_script)
        
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
