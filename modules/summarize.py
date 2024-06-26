import re
import nltk
import heapq

def preprocess_article(article_content):
    """
    Preprocesses the given article content by removing numeric references,
    extra whitespace, and non-alphabetic characters.

    Args:
        article_content (str): The raw content of the article.

    Returns:
        tuple: A tuple containing the preprocessed article content and the formatted article content.
    """
    article_content = re.sub(r'\[[0-9]*\]', ' ', article_content)
    article_content = re.sub(r'\s+', ' ', article_content)
    formatted_article_content = re.sub('[^a-zA-Z]', ' ', article_content )

    return article_content, formatted_article_content

def filter_promotional_sentences(text):
    """
    Filters out sentences containing promotional or commercial content.

    Args:
        text (str): The text to filter.

    Returns:
        str: The filtered text without promotional sentences.
    """
    promo_keywords = [ 'compensated', 'promotional', 'sponsored', 'on this site', 'on this website', 'subscription']

    promo_pattern = r'\b(?:{})\b'.format('|'.join(promo_keywords))

    filtered_sentences = []
    for sentence in nltk.sent_tokenize(text):
        if not re.search(promo_pattern, sentence, flags=re.IGNORECASE):
            filtered_sentences.append(sentence)

    return ' '.join(filtered_sentences)

def get_most_used_words(formatted_text):
    """
    Computes word frequencies in the formatted text, excluding stopwords.

    Args:
        formatted_text (str): The cleaned and formatted text of the article.

    Returns:
        dict: A dictionary where keys are words and values are their normalized frequencies.
    """
    if len(formatted_text) < 50:
        return {"null": 0.1}
    stopwords = nltk.corpus.stopwords.words('english')
    word_frequencies = {}
    for word in nltk.word_tokenize(formatted_text):
        if word not in stopwords:
            if word not in word_frequencies.keys():
                word_frequencies[word] = 1
            else:
                word_frequencies[word] += 1

    maximum_frequency = max(word_frequencies.values())
    for word in word_frequencies.keys():
        word_frequencies[word] = (word_frequencies[word]/maximum_frequency)
    return word_frequencies

def get_most_sentence_scores(text, word_frequencies):
    """
    Calculates sentence scores based on word frequencies.

    Args:
        text (str): The text to be scored.
        word_frequencies (dict): Dictionary of word frequencies.

    Returns:
        dict: A dictionary where keys are sentences and values are their scores.
    """
    sentence_scores = {}
    sentence_list = nltk.sent_tokenize(text)
    if len(word_frequencies.keys()) == 1:
        return {"null": 0.1}

    for sent in sentence_list:
        for word in nltk.word_tokenize(sent.lower()):
            if word in word_frequencies.keys():
                if len(sent.split(' ')) < 30:
                    if sent not in sentence_scores.keys():
                        sentence_scores[sent] = word_frequencies[word]
                    else:
                        sentence_scores[sent] += word_frequencies[word]
    return sentence_scores

def summarize_text(sentence_scores, number_of_sentences):
    """
    Generates a summary from sentence scores using heapq to get top sentences.

    Args:
        sentence_scores (dict): Dictionary of sentence scores.
        number_of_sentences (int): Number of sentences to include in the summary.

    Returns:
        str: The generated summary text.
    """
    if len(sentence_scores.keys()) == 1:
        return ""
    elif(len(sentence_scores.keys()) < number_of_sentences + 5):
        number_of_sentences = int(round(number_of_sentences / 1.5, 0))
    summary_sentences = heapq.nlargest(number_of_sentences, sentence_scores, key=sentence_scores.get)
    summary = ' '.join(summary_sentences)
    return summary
    
def apply_summarization_to_article(site_content, number_of_sentences):
    """
    Applies summarization pipeline to a single article's content.

    Args:
        site_content (str): The content of the article.
        number_of_sentences (int): Desired number of sentences in the summary.

    Returns:
        tuple: A tuple containing the summarized text and word frequencies used.
    """
    # Filter out promotional sentences
    filtered_content = filter_promotional_sentences(site_content)

    # Split filtered content into segments and summarize each segment
    site_content_segments = re.split(r'(?<=[.!?]) +', filtered_content)
    limit = len(site_content_segments) // 3
    processed_list = [
        " ".join(site_content_segments[:int(limit)]), 
        " ".join(site_content_segments[int(limit):int(2 * limit)]),
        " ".join(site_content_segments[int(2 * limit):])
    ]

    for index, element in enumerate(processed_list):
        processed_text, formatted_text = preprocess_article(element)
        words = get_most_used_words(formatted_text)
        sentences = get_most_sentence_scores(processed_text, words)
        processed_list[index] = summarize_text(sentences, int(round(number_of_sentences / 3)))

    return "\n".join(processed_list), words

def apply_summarization_article_on_trend(contents, number_of_sentences):
    """
    Applies summarization pipeline to a list of article contents.

    Args:
        contents (list): List of article contents.
        number_of_sentences (int): Desired number of sentences in the final summarized text.

    Returns:
        tuple: A tuple containing the summarized text and word frequencies used.
    """
    summarizations = []
    for index, content in enumerate(contents):
        content = contents[index]
        summarizations.append(apply_summarization_to_article(content, number_of_sentences)[0])
    summarized_text = "\n".join(summarizations)

    return apply_summarization_to_article(summarized_text, number_of_sentences)
