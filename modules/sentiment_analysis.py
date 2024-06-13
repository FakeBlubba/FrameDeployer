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

