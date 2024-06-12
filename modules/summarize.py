import re
import nltk
import heapq

# Returns text preprocessed (hope)
def preprocess_article(article_content):
    article_content = re.sub(r'\[[0-9]*\]', ' ', article_content)
    article_content = re.sub(r'\s+', ' ', article_content)
    formatted_article_content = re.sub('[^a-zA-Z]', ' ', article_content )

    return article_content, formatted_article_content

def get_most_used_words(formatted_text):
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
    if len(sentence_scores.keys()) == 1:
        return ""
    elif(len(sentence_scores.keys()) < number_of_sentences + 5):
        number_of_sentences = int(round(number_of_sentences / 1.5, 0))
    summary_sentences = heapq.nlargest(number_of_sentences, sentence_scores, key=sentence_scores.get)
    summary = ' '.join(summary_sentences)
    return summary
    
def apply_summarization_to_article(site_content, number_of_sentences):
    print(site_content, "\n\n\n\n")
    site_content = re.split(r'(?<=[.!?]) +', site_content)
    print("\n\n\n\n\n")
    print(len(site_content))
    limit = len(site_content) // 3
    print(limit)
    processed_list = [
        " ".join(site_content[:int(limit)]), 
        " ".join(site_content[int(limit):int(2 * limit)]),
        " ".join(site_content[int(2 * limit):])
        ]
    for index, element in enumerate(processed_list):
        
        processed_text, formatted_text = preprocess_article(element)
        words = get_most_used_words(formatted_text)
        sentences = get_most_sentence_scores(processed_text, words)
        processed_list[index] = summarize_text(sentences, int(round(number_of_sentences / 3)))    
    return "\n".join(processed_list), words

def apply_summarization_article_on_trend(contents, number_of_sentences):
    summarizations = []
    for index, content in enumerate(contents):
        content = contents[index]
        summarizations.append(apply_summarization_to_article(content, number_of_sentences)[0])
    summarized_text = "\n".join(summarizations)

    return apply_summarization_to_article(summarized_text, number_of_sentences)
