import requests
import os
from datetime import datetime
import random
from nltk.tokenize import word_tokenize
from nltk import pos_tag
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from collections import Counter


def simplified_lesk(context_sentence, synsets):
    context = set(word_tokenize(context_sentence))
    max_overlap = 0
    best_sense = None

    for sense in synsets:
        signature = set(word_tokenize(sense.definition()))
        for example in sense.examples():
            signature.update(word_tokenize(example))
        
        overlap = len(context.intersection(signature))
        if overlap > max_overlap:
            max_overlap = overlap
            best_sense = sense

    return best_sense

def get_synonyms(word):
    synonyms = set()
    for syn in wn.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())  # Aggiunge i sinonimi trovati al set
    return list(synonyms)

def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return wn.ADJ
    elif treebank_tag.startswith('V'):
        return wn.VERB
    elif treebank_tag.startswith('N'):
        return wn.NOUN
    elif treebank_tag.startswith('R'):
        return wn.ADV
    else:
        return None

def main_noun_from_sentence(sentence):
    tokens = word_tokenize(sentence)
    filtered_tokens = [word for word in tokens if word.lower() not in stopwords.words('english')]
    tagged = pos_tag(filtered_tokens)
    nouns = [word for word, tag in tagged if get_wordnet_pos(tag) == wn.NOUN]
    noun_freq = Counter(nouns)
    if noun_freq:
        most_common_noun = noun_freq.most_common(1)[0][0]
        return most_common_noun
    else:
        return "No dominant noun found"

def get_wiki_commons_image_url(trend_name, text, min_height, num_images):
    urls = []
    search_term = trend_name
    main_noun = main_noun_from_sentence(trend_name)
    syns = wn.synsets(main_noun)
    best_sense = simplified_lesk(text, syns)
    if best_sense:
        search_term = str(best_sense.lemmas()[0].name())  # Assicurati che questo sia corretto
    API_ENDPOINT = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrnamespace": 6,
        "gsrsearch": search_term,
        "gsrlimit": 50,
        "prop": "imageinfo",
        "iiprop": "url|size|mime",  # Aggiungi "mime" per ottenere il tipo MIME dell'immagine
    }
    response = requests.get(API_ENDPOINT, params=params)
    data = response.json()
    if "query" in data:
        pages = data["query"]["pages"]
        for index, element in enumerate(pages):
            image_info = pages[element]["imageinfo"][0]
            height = image_info.get("height")
            mime_type = image_info.get("mime")  # Ottiene il tipo MIME dell'immagine
            if height >= min_height and mime_type == "image/jpeg":  # Usa "image/jpeg" per le immagini JPEG
                urls.append(image_info["url"])
                if len(urls) >= num_images:
                    break
    return urls


def download_image(image_url, folder_path, image_name):
    save_path = os.path.join(folder_path, image_name + ".jpg")
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    try:
        with requests.get(image_url, headers=headers, stream=True) as response:
            response.raise_for_status()  # Questo solleverà un'eccezione per codici di errore HTTP
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"Download completed: {image_name}.jpg")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # ad esempio, risposta 404 o 500
    except Exception as err:
        print(f"An error occurred: {err}")

def searchAndDownloadImage(trend, text, min_height=1080, number_of_images=16):
    urls = get_wiki_commons_image_url(trend, text, min_height, number_of_images)
    main_noun = main_noun_from_sentence(trend)
    syns = get_synonyms(main_noun)
    if not urls:
        print("No suitable images found. Trying synonyms.")
        for syn in syns:
            urls.extend(get_wiki_commons_image_url(syn, text, min_height, number_of_images))
            if len(urls) >= number_of_images:
                break
        urls = urls[:number_of_images]  
    if not urls:
        print("Unable to find images for the given trend and its synonyms.")
        return None

    date_string = datetime.now().strftime("%d-%m-%Y")
    folder_path = os.path.join("media", f"{trend}{date_string}")
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    output = []
    for index, url in enumerate(urls):
        download_image(url, folder_path, f"image_{index + 1}")
        output.append(os.path.join(folder_path, f"image_{index + 1}.jpg"))

    return output

def selectMusicByEmotion(emotion):
    folder_path = f"media/music/{emotion}"  
    if folder_path.endswith('0'):
        random_choice = random.choice([-1, 1])
        folder_path = folder_path[:-1] + str(random_choice)

    files = [f for f in os.listdir(folder_path) if f.endswith('.mp3')]

    if not files:
        return None 

    selected_file = random.choice(files)
    cc_info = ""

    with open("media/music/CC.txt", "r") as cc_file:
        cc_list = [line for line in cc_file]
        for index, line in enumerate(cc_list):
            file_identifier = selected_file.rsplit('.', 1)[0].rsplit("[",1)[0]  
            if file_identifier in line:  
                cc_info += f"{line}{cc_list[index + 1]}{cc_list[index + 2]}{cc_list[index + 3]}"


    result = {
        "path": os.path.join(folder_path, selected_file),
        "cc": cc_info.strip()
    }

    return result