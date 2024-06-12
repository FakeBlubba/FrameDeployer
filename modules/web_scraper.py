from bs4 import BeautifulSoup
from pytrends.request import TrendReq
from duckduckgo_search import DDGS
import requests
from requests.exceptions import RequestException

# Returns an array of trends
def get_trends():
    pytrend = TrendReq()
    return pytrend.trending_searches().iloc[:, 0].tolist()

# Returns a list of articles based on a topic
def get_articles_on_topic_excluding_blacklist(topic, max_searches, blacklist):
    with DDGS() as ddgs:
        results = ddgs.text(topic, max_results=max_searches, safesearch="on")
        filtered_results = [result for result in results if result and not any(blacklisted in result.get("href", "") for blacklisted in blacklist)]
        return filtered_results

# Returns string of text with the text of the article  
def get_site_content(url):
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
        print(f"Website not reachable: {e}")
        return None

def get_trend_contents(trend_number, number_of_articles_to_read):
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
