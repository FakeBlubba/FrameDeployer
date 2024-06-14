import os
import shutil

import modules.web_scraper
import modules.editing
import modules.sentiment_analysis
import modules.subtitles
import modules.text_to_speech
import modules.summarize
import modules.media_finder

class ResourceManager:
    def __init__(self, trend_number, number_of_articles_to_read = 10, text_articles=8, text_length=7, desc_articles=5, desc_length=3, language="English"):
        """
        Initializes the ResourceManager with parameters for generating resources.

        Args:
        - trend_number (int): Index of the trend to retrieve.
        - number_of_articles_to_read (int): Number of articles to read for main text.
        - text_articles (int): Number of articles to use for text summarization.
        - text_length (int): Number of sentences to include in main text summarization.
        - desc_articles (int): Number of articles to use for description summarization.
        - desc_length (int): Number of sentences to include in description summarization.
        - language (str): Language for text-to-speech conversion.
        """
        self.trend_number = trend_number
        self.number_of_articles_to_read = number_of_articles_to_read
        self.text_articles = text_articles
        self.text_length = text_length
        self.desc_articles = desc_articles
        self.desc_length = desc_length
        self.language = language

    def generate_resources(self):
        """
        Generates resources including text, audio, subtitles, and media for a given trend.

        Returns:
        - dict: Dictionary containing generated resources.
        """
        trend = modules.web_scraper.get_trends()
        contents = modules.web_scraper.get_trend_contents(self.trend_number, self.number_of_articles_to_read)
        desc_contents_scrapped = modules.web_scraper.get_trend_contents(self.trend_number, self.desc_articles)
        if(not contents):
            print("Error: during the searching for the selected trend.")
            return False
        
        text_script, tags = modules.summarize.apply_summarization_article_on_trend(contents, self.text_length)
        description, _ = modules.summarize.apply_summarization_article_on_trend(desc_contents_scrapped, self.desc_length)
        
        if(not text_script):
            print("Error: during the summarization.")
            return False
        
        images = modules.media_finder.searchAndDownloadImage(trend[self.trend_number], text_script)
        
        if not images or not text_script:
            print("Error: during the search of images.")
            return False
        
        sentiment_analysis_output = modules.sentiment_analysis.get_summarization_emotion(text_script)
        if not sentiment_analysis_output:
            print("Error: during the sentiment analysis output.")
            return False

        #   Setting up paths
        part = str(images[0].split("/"))[:-1].split("\\")
        path = os.path.join(part[0][2:], part[2])
        music_folder_path = os.path.join(part[0][2:], "music")
        
        #   Setting up tags for description
        tags = [f"#{tag}" for index, tag in enumerate(tags) if index < 15]
        tags = " ".join(tags)
        
        #   Setting up the music based on the emotion
        music_path = modules.media_finder.selectMusicByEmotion(sentiment_analysis_output, music_folder_path)
        if not music_path:
            print("Error: selecting the music path.")
            shutil.rmtree(path)
            return False
        
        #   Setting up the tts audio file
        audio_file = modules.text_to_speech.get_text_to_speech(text_script, path, self.language)
        
        if not audio_file:
            print("Error: creating the Text-To-Speech.")
            shutil.rmtree(path)
            return False
        
        #   Converting Text-To-Speech into captions
        srt_file = modules.subtitles.generate_srt(audio_file, path)
        
        if not srt_file:
            print("Error: creating the Text-To-Speech.")
            shutil.rmtree(path)
            return False
        
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
