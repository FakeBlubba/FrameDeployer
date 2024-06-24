import requests
import os
import random
import modules.file_manager
from nltk.tokenize import word_tokenize
from nltk import pos_tag
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from collections import Counter


def simplified_lesk(context_sentence, synsets):
    """
    Performs simplified Lesk algorithm to disambiguate word senses.

    Args:
        context_sentence (str): The context sentence for disambiguation.
        synsets (list): List of WordNet synsets for a specific word.

    Returns:
        nltk.corpus.reader.wordnet.Synset or None: The best sense found or None.
    """
    context = set(word_tokenize(context_sentence))
    max_overlap = 0
    best_sense = None
    second_best_sense = None

    for sense in synsets:
        signature = set(word_tokenize(sense.definition()))
        for example in sense.examples():
            signature.update(word_tokenize(example))
        
        overlap = len(context.intersection(signature))
        if overlap > max_overlap:
            if(best_sense is not None):
                second_best_sense = best_sense
            max_overlap = overlap
            best_sense = sense

    return [best_sense, second_best_sense]

def get_synonyms(word):
    """
    Retrieves synonyms for a given word using WordNet.

    Args:
        word (str): The word to find synonyms for.

    Returns:
        list: A list of synonyms for the given word.
    """
    synonyms = set()
    for syn in wn.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())
    return list(synonyms)

def get_wordnet_pos(treebank_tag):
    """
    Maps NLTK's POS tags to WordNet's POS tags.

    Args:
        treebank_tag (str): The POS tag from NLTK.

    Returns:
        str or None: The corresponding WordNet POS tag or None if not found.
    """
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
    """
    Extracts the main noun from a sentence using POS tagging and WordNet.

    Args:
        sentence (str): The input sentence.

    Returns:
        str: The most common noun found in the sentence.
    """
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

def get_wiki_commons_media_url(search_term, text, num_media, min_height, type = "imageinfo"):
    """
    Retrieves media URLs from Wikimedia Commons based on a search_term and a type of media.

    Args:
        search_term (str): The text context associated with the trend.
        text (str): The text where the trend_name is found.
        num_media (int): The number of media requested.
        min_height (int): The minimum height of the media.
        type (str): The text of the type of media imageinfo or video.
    Returns:
        list: A list of URLs of the retrieved media.
    """
    API_ENDPOINT = "https://commons.wikimedia.org/w/api.php"
    urls = []
    mime_type_r = "image/jpeg" if type == "imageinfo" else "video/mp4"
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrnamespace": 6,
        "gsrsearch": search_term,
        "gsrlimit": 50,
        "prop": type,
        "iiprop": "url|size|mime", 
    }
    response = requests.get(API_ENDPOINT, params=params)
    data = response.json()
    if "query" in data:
        pages = data["query"]["pages"]
        for index, element in enumerate(pages):
            image_info = pages[element][type][0]
            height = image_info.get("height")
            mime_type = image_info.get("mime")
            if height >= min_height and mime_type == mime_type_r: 
                urls.append(image_info["url"])
                if len(urls) >= num_media:
                    break
    return urls

def get_search_term(trend_name, text):
    """
    Retrieves the search term based on the trend name thanks to lesk implementation.

    Args:
        trend_name (str): The trend or topic name.
        text (str): The text where the trend_name is found.

    Returns:
        str: The search term.
    """
    main_noun = main_noun_from_sentence(trend_name)
    syns = wn.synsets(main_noun)
    best_senses = simplified_lesk(text, syns)

    if(best_senses[1] is not None):
        return str(best_senses[0].lemmas()[0].name() + " " + best_senses[1].lemmas()[0].name())
    elif(best_senses[0] is not None):
        return str(best_senses[0].lemmas()[0].name())
    else:
        return trend_name

def get_wiki_commons_image_url(trend_name, text, min_height, num_images):
    """
    Retrieves image URLs from Wikimedia Commons based on a trend and associated text.

    Args:
        trend_name (str): The trend or topic name.
        text (str): The text where the trend_name is found.
        min_height (int): Minimum height requirement for images.
        num_images (int): Number of images to retrieve.

    Returns:
        list: A list of URLs of the retrieved images.
    """
    search_term = get_search_term(trend_name, text)
    return get_wiki_commons_media_url(search_term, text, num_images, min_height)

def get_wiki_commons_video_url(trend_name, text, min_height=720, num_videos=5, limit = 10):
    """
    Searches Wikimedia Commons for video URLs based on a trend and associated text.

    Args:
        trend_name (str): The trend or topic name.
        text (str): The text where the trend_name is found.
        min_height (int): Minimum height requirement for videos.
        num_videos (int): Number of videos to retrieve.

    Returns:
        list: A list of URLs of the retrieved videos.
    """
    API_ENDPOINT = "https://commons.wikimedia.org/w/api.php"

    search_term = get_search_term(trend_name, text)
    params = {
    "action": "query",
    "format": "json",
    "list": "search",
    "srsearch": search_term,
    "srnamespace": "6",  
    "srlimit": limit,
    "srprop": "snippet|titlesnippet",
    "srinfo": "totalhits",
    "sroffset": 0,
    "srenablerewrites": "1",
    "srwhat": "text",
    }

    response = requests.get(API_ENDPOINT, params=params)
    data = response.json()

    videos = []
    if "query" in data:
        for result in data["query"]["search"]:
            if result["title"].lower().endswith('.mp4'):
                videos.append({
                    "title": result["title"],
                    "snippet": result["snippet"],
                })
    video_titles = [video['title'] for video in videos]
    urls = []
    for title in video_titles:
        params = {
            "action": "query",
            "format": "json",
            "prop": "imageinfo",
            "titles": title,
            "iiprop": "url",
        }

        response = requests.get(API_ENDPOINT, params=params)
        data = response.json()

        pages = data.get("query", {}).get("pages", {})
        for page_id, page_data in pages.items():
            if "imageinfo" in page_data:
                for image_info in page_data["imageinfo"]:
                    urls.append(image_info["url"])

    return urls


def download_media(media_url, folder_path, media_name, extension = ".jpg"):
    """
    Downloads an media from a URL and saves it to a specified folder.

    Args:
        media_url (str): The URL of the media to download.
        folder_path (str): The folder path to save the downloaded media.
        media_name (str): The name to assign to the downloaded media.
        extension (str): The file extension requested.
    """
    save_path = os.path.join(folder_path, media_name + extension)
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    try:
        with requests.get(media_url, headers=headers, stream=True) as response:
            response.raise_for_status()  
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  
    except Exception as err:
        print(f"An error occurred: {err}")

def search_media_with_synonyms(trend_name, text, min_height, number_of_media, get_wiki_commons_func):
    """
    Searches for media URLs from Wikimedia Commons using synonyms of the trend name.

    Args:
        trend_name (str): The trend or topic name.
        text (str): The text where the trend_name is found.
        min_height (int): Minimum height requirement for images.
        number_of_media (int): Number of media to retrieve.
        get_wiki_commons_func (func): choose the func between get_wiki_commons_image and get_wiki_commons_video

    Returns:
        list: A list of URLs of the retrieved media.
    """
    urls = []
    main_noun = main_noun_from_sentence(trend_name)
    syns = get_synonyms(main_noun)

    for syn in syns:
        urls.extend(get_wiki_commons_func(syn, text, min_height, number_of_media))
        if len(urls) >= number_of_media:
            break

    return urls

def search_and_download_media(trend, text, min_height=1080, number_of_media=16):
    """
    Searches for media related to a trend, downloads them, and returns their paths.

    Args:
        trend (str): The trend or topic to search media for.
        min_height (int): Minimum height requirement for media.
        number_of_media (int): Number of media to download.

    Returns:
        list: List of paths where the downloaded media are saved.
    """

    num_videos = number_of_media // 8
    urls = search_media_with_synonyms(trend, text, min_height, number_of_media - num_videos, get_wiki_commons_image_url)
    #urls = search_media_with_synonyms(trend, text, min_height, number_of_media, get_wiki_commons_image_url)

    extension = ".jpg"
    urls2 = search_media_with_synonyms(trend, text, min_height, num_videos, get_wiki_commons_video_url)
    extension2 = ".mp4"
    if not urls:
        print("Unable to find images for the given trend and its synonyms.")
        #urls.extend(search_media_with_synonyms(trend, text, min_height, number_of_media - num_videos, get_wiki_commons_video_url))

    if not urls2:
        print("Unable to find videos for the given trend and its synonyms.")

        urls.extend(search_media_with_synonyms(trend, text, min_height, num_videos, get_wiki_commons_image_url))
    
    if not urls:
        print("Unable to find media for the given trend and its synonyms.")
        return None

    folder_path = modules.file_manager.create_media_folder(trend)

    output = []
    for index, url in enumerate(urls2):
        download_media(url, folder_path, f"media_{index + 1}", extension2)
        output.append(os.path.join(folder_path, f"media_{index + 1}{extension2}"))
    for index, url in enumerate(urls):
        download_media(url, folder_path, f"media_{index + 1}")
        output.append(os.path.join(folder_path, f"media_{index + 1}{extension}"))

    return output

def selectMusicByEmotion(emotion, folder_path):
    """
    Selects a random music file based on the provided emotion.

    Args:
        emotion (str): The emotion to select music for.

    Returns:
        dict or None: Dictionary containing the path of the selected music file
                        and associated Creative Commons (CC) license information.
                        Returns None if no suitable music files are found.
    """
    if emotion == "0":
        emotion = random.choice([-1, 1])
        
    music_folder = os.path.join(folder_path, str(emotion))

    files = [f for f in os.listdir(music_folder) if f.endswith('.mp3')]

    if not files:
        return None 

    selected_file = random.choice(files)
    cc_info = ""

    with open(os.path.join(folder_path, "CC.txt"), "r") as cc_file:
        cc_list = [line for line in cc_file]
        for index, line in enumerate(cc_list):
            file_identifier = selected_file.rsplit('.', 1)[0].rsplit("[",1)[0]  
            if file_identifier in line:  
                cc_info += f"{line}{cc_list[index + 1]}{cc_list[index + 2]}{cc_list[index + 3]}"


    result = {
        "path": os.path.join(folder_path, str(emotion), selected_file),
        "cc": cc_info.strip()
    }

    return result