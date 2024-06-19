import os
import shutil
import modules.web_scraper
import modules.editing
import modules.sentiment_analysis
import modules.subtitles
import modules.text_to_speech
import modules.summarize
import modules.media_finder
import modules.file_manager

class ResourceManager:
    def __init__(self, trend_number, number_of_articles_to_read=10, text_articles=8, text_length=7, desc_articles=5, desc_length=3, language="English"):
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
        
        if not contents:
            print(f"Error: Unable to retrieve contents for trend {trend[self.trend_number]}.")
            return None
        
        text_script, tags = modules.summarize.apply_summarization_article_on_trend(contents, self.text_length)
        description, _ = modules.summarize.apply_summarization_article_on_trend(desc_contents_scrapped, self.desc_length)
        
        if not text_script:
            print("Error: Summarization failed.")
            return None
        
        images = modules.media_finder.searchAndDownloadImage(trend[self.trend_number], text_script)
        
        if not images:
            print("Error: Image search/download failed.")
            return None
        
        sentiment_analysis_output = modules.sentiment_analysis.get_summarization_emotion(text_script)
        
        if not sentiment_analysis_output:
            print("Error: Sentiment analysis failed.")
            return None

        part = str(images[0].split("/"))[:-1].split("\\")
        path = os.path.join(part[0][2:], part[2])
        music_folder_path = os.path.join(part[0][2:], "music")
        tags = [f"#{tag}" for index, tag in enumerate(tags) if index < 25]
        tags = " ".join(tags)
        music_path = modules.media_finder.selectMusicByEmotion(sentiment_analysis_output, music_folder_path)
        
        if not music_path:
            print("Error: Music selection failed.")
            shutil.rmtree(path)
            return None
        
        audio_file = modules.text_to_speech.get_text_to_speech(text_script, path, self.language)
        
        if not audio_file:
            print("Error: Text-to-Speech conversion failed.")
            shutil.rmtree(path)
            return None
        
        srt_file = modules.subtitles.generate_srt(audio_file, path)
        
        if not srt_file:
            print("Error: Subtitle generation failed.")
            shutil.rmtree(path)
            return None
        
        output = {
            "Trend": trend,
            "TextScript": text_script,
            "Audio": audio_file,
            "subs": srt_file,
            "Description": description,
            "Tags": tags + "#IA",
            "Images": images,
            "MusicPath": music_path,
            "dir": path
        }
        
        return output

    def main(self):
        output = self.generate_resources()
        
        if output:
            modules.editing.create_video_with_data(output)
            modules.file_manager.delete_files_except_mp4(output["dir"])
            description_text = f"{output['Description']}\n\n🎵 Music: {output['MusicPath']['cc']}\n\n\n{output['Tags']}"
            print(description_text)
            return description_texta
        
        return None
