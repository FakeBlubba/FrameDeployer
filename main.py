import scraping_and_summarization
import media_finder
import sentiment_analysis
import text_to_speech

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
    print(images)
    part = str(images[0].split("/"))[1:-1].split("\\")[:-1]
    path = "\\".join(part)

    tags = [f"#{tag}" for index, tag in enumerate(tags) if index < 15]
    tags = " ".join(tags)
    music_path = ""
    music_path = media_finder.selectMusicByEmotion(sentiment_analysis.get_summarization_emotion(text_script))


    audio_file = text_to_speech.get_text_to_speech(text_script, path, language)
    return {
        "Trend": trend, 
        "TextScript": text_script, 
        "Audio": audio_file,
        "Description": description,
        "Tags": tags,
        "Images": images,
        "MusicPath": music_path
        }
def main():
    output = generate_resources(0)
    if output != None:
        print(output)
        return
    print("NIENTE DA FARE PORCO DIO")
main()
