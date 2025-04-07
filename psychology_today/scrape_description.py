from sumy.parsers.html import HtmlParser
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.tokenizers import Tokenizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

LANGUAGE = "english"

def scrape_description(urls: list[str], target_name: str):
    """
    Fetch webpage text, extract sentences mentioning the target name,
    and summarize them into one concise sentence.
    """
    for url in urls:
        try:
            # Use the PlaintextParser to parse the combined text (no need to pass tokenizer explicitly)
            parser = HtmlParser.from_url(url, Tokenizer(LANGUAGE))

            stemmer = Stemmer(LANGUAGE)

            summarizer = Summarizer(stemmer)
            summarizer.stop_words = get_stop_words(LANGUAGE)

            for sentence in summarizer(parser.document, 1):
                print(sentence) # Summarize to 1 sentence

        except Exception as e:
            print(f"Error processing {url}: {e}")

if __name__ == "__main__":
    # Fetch top URLs using Google Search
    from googlesearch import search
    search_query = "Amber Behrouzvaziri"
    urls = [url for url in search(search_query, num_results=5)]

    scrape_description(urls, search_query)
