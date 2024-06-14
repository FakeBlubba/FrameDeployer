from textblob import TextBlob

def get_summarization_emotion(summarization):
    """
    Analyzes the sentiment polarity of a summarization using TextBlob.

    Args:
        summarization (str): The text summarization to analyze.

    Returns:
        int: 1 if the sentiment polarity is positive, -1 if negative, 0 if neutral.
    """
    blob = TextBlob(summarization)

    sentiment = blob.sentiment

    if sentiment.polarity > 0:
        return 1
    elif sentiment.polarity < 0:
        return -1
    else:
        return 0
    
    
def select_emoji_based_on_description(description):
    """
    Applies the summarization pipeline to a list of article contents.

    Args:
    contents (list): List of article contents.
    number_of_sentences (int): Desired number of sentences in the final summarized text.

    Returns:
    tuple: A tuple containing the summarized text and word frequencies used.
    """
    emoji_dict = {
        "love": "❤️",
        "happy": "😊",
        "sad": "😢",
        "excited": "🤩",
        "angry": "😠",
        "surprised": "😲",
        "funny": "😂",
        "news": "📰",
        "sports": "⚽",
        "music": "🎵",
        "food": "🍔",
        "travel": "✈️",
        "fashion": "👗",
        "technology": "💻",
        "health": "🏥"
    }
    
    description_lower = description.lower()
    
    for keyword, emoji in emoji_dict.items():
        if keyword in description_lower:
            return emoji
    
    return "🤖"

