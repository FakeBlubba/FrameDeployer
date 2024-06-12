from pathlib import Path
import sys
import os

if __name__ != '__main__':
    import modules.media_finder
    import modules.scraping_and_summarization
    import modules.sentiment_analysis
    import modules.text_to_speech
    import modules.subtitles
    import modules.editing
    import modules.resourcesGenerator
else:
    import scraping_and_summarization
    import media_finder
    import sentiment_analysis
    import text_to_speech
    import subtitles
    import editing
    import resourcesGenerator