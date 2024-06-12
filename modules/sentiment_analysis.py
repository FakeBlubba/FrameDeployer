from textblob import TextBlob

def get_summarization_emotion(summarization):
    
    blob = TextBlob(summarization)

    sentimento = blob.sentiment

    if sentimento.polarity > 0:
        return 1
    elif sentimento.polarity < 0:
        return -1
    else:
        return 0

