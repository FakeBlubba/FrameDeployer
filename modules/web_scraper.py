from bs4 import BeautifulSoup
from pytrends.request import TrendReq
from duckduckgo_search import DDGS
import requests
from requests.exceptions import RequestException

def get_trends():
    """
    Retrieves current trending searches using Google Trends API.

    Returns:
        list: List of trending search topics.
    """
    pytrend = TrendReq()
    return pytrend.trending_searches().iloc[:, 0].tolist()

def get_articles_on_topic_excluding_blacklist(topic, max_searches, blacklist):
    """
    Searches for articles related to a given topic while excluding URLs in the blacklist.

    Args:
        topic (str): The topic of interest for article searches.
        max_searches (int): Maximum number of search results to fetch.
        blacklist (list): List of URLs to exclude from search results.

    Returns:
        list: List of filtered search results (articles).
    """
    with DDGS() as ddgs:
        results = ddgs.text(topic, max_results=max_searches, safesearch="on")
        filtered_results = [result for result in results if result and not any(blacklisted in result.get("href", "") for blacklisted in blacklist)]
        return filtered_results

def get_site_content(url):
    """
    Retrieves and extracts the textual content from a given URL.

    Args:
        url (str): URL of the article to fetch and parse.

    Returns:
        str or None: Extracted text content of the article, or None if failed to fetch.
    """
    try:
        response = requests.get(url, timeout=10)  
        response.raise_for_status()  
        
        soup = BeautifulSoup(response.text, 'html.parser')
        article_content = soup.find_all('p') 
        output = "\n\n".join(part.get_text() for part in article_content[1:-1])
        if not output.strip():
            return None
        return output
    
    except RequestException as e:
        print(f"Article website not reachable, searching more... .")
        return None

def get_trend_contents(trend_number, number_of_articles_to_read):
    """
    Retrieves the contents of articles related to a specific trending topic.

    Args:
        trend_number (int): Index of the trending topic to fetch articles for.
        number_of_articles_to_read (int): Desired number of articles to fetch.

    Returns:
        list: List of article contents fetched for the trending topic.
    """
    black_list = ["https://en.wikipedia.org", "https://www.wikipedia.org"]
    trends = get_trends()
    trend = trends[trend_number]

    articles = []
    contents = []

    while len(contents) < number_of_articles_to_read:
        remaining_articles_to_fetch = number_of_articles_to_read - len(contents)
        new_articles = get_articles_on_topic_excluding_blacklist(trend, remaining_articles_to_fetch, black_list)

        for article in new_articles:
            content = get_site_content(article.get("href", ""))
            if content:
                articles.append(article)
                contents.append(content)

        if not new_articles:  
            break

    return contents[:number_of_articles_to_read]
