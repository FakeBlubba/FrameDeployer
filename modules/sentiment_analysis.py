from textblob import TextBlob

def get_summarization_emotion(summarization):
    
    blob = TextBlob(summarization)

    sentiment = blob.sentiment

    if sentiment.polarity > 0:
        return 1
    elif sentiment.polarity < 0:
        return -1
    else:
        return 0

