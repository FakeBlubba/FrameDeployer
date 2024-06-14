import unittest
import modules.summarize as summarize
import modules.web_scraper as web_scraper
import modules.sentiment_analysis as sentiment_analysis
import modules.media_finder as media_finder
class TestWebScraper(unittest.TestCase):

    def test_get_trends(self):
        trends = web_scraper.get_trends()
        self.assertTrue(len(trends) > 0)  

    def get_articles_on_topic_excluding_blacklist(self):
        topic = "Artificial Intelligence"
        max_searches = 5
        articles = web_scraper.get_articles_on_topic(topic, max_searches)
        self.assertTrue(len(articles) > 0)  

    def test_get_site_content(self):
        url = "https://en.wikipedia.org/wiki/Artificial_intelligence"
        content = web_scraper.get_site_content(url)
        self.assertTrue(len(content) > 0)

class TestSummarization(unittest.TestCase):

    def test_preprocess_article(self):
        article_content = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer nec odio. Praesent libero."
        processed, formatted = summarize.preprocess_article(article_content)
        self.assertEqual(processed, article_content)
        self.assertNotEqual(formatted, article_content)  

    def test_get_most_used_words(self):
        formatted_text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
        word_frequencies = summarize.get_most_used_words(formatted_text)
        self.assertTrue("Lorem" in word_frequencies)

    def test_get_most_sentence_scores(self):
        text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
        word_frequencies = {"Lorem": 0.5, "ipsum": 0.3, "dolor": 0.2}
        sentence_scores = summarize.get_most_sentence_scores(text, word_frequencies)
        self.assertTrue(len(sentence_scores) > 0)

    def test_summarize_text(self):
        sentence_scores = {"Sentence 1": 0.5, "Sentence 2": 0.3, "Sentence 3": 0.2}
        summary = summarize.summarize_text(sentence_scores, 2)
        self.assertTrue(len(summary) > 0)

    def test_apply_summarization_to_article(self):
        site_content = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
        number_of_sentences = 2
        summarized_text, _ = summarize.apply_summarization_to_article(site_content, number_of_sentences)
        self.assertTrue(len(summarized_text) > 0)

    def test_apply_summarization_article_on_trend(self):
        contents = [
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
            "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur."
        ]
        number_of_sentences = 2
        summarized_text, _ = summarize.apply_summarization_article_on_trend(contents, number_of_sentences)
        self.assertTrue(len(summarized_text) > 0) 

class TestSentimentAnalysis(unittest.TestCase):

    def test_get_summarization_emotion_positive(self):
        summarization = "I really enjoyed reading this article. It was very informative and well-written."
        emotion = sentiment_analysis.get_summarization_emotion(summarization)
        self.assertEqual(emotion, 1)

    def test_get_summarization_emotion_negative(self):
        summarization = "This article was poorly written and lacked useful information."
        emotion = sentiment_analysis.get_summarization_emotion(summarization)
        self.assertEqual(emotion, -1)

class TestMediaFinder(unittest.TestCase):
    def test_searchAndDownloadImage(self):
        trend = "Apollo"
        text = "Sample text for searching images"
        images = media_finder.searchAndDownloadImage(trend, text)
        self.assertTrue(images)
        self.assertIsInstance(images, list)
        self.assertTrue(all(isinstance(img, str) for img in images))

if __name__ == '__main__':
    unittest.main()

if __name__ == '__main__':
    unittest.main()
