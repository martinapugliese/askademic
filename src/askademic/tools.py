import logging
import time
from datetime import datetime
from io import BytesIO

import feedparser
import pymupdf
import requests

from askademic.constants import ARXIV_BASE_URL
from askademic.utils import list_categories, organise_api_response_as_dataframe

today = datetime.now().strftime("%Y-%m-%d")

logging.basicConfig(level=logging.INFO, filename=f"logs/{today}_logs.txt")
logger = logging.getLogger(__name__)


def get_categories() -> dict:

    # these are from page "https://arxiv.org/category_taxonomy"
    # alternative would be to scrape the page but it's not a good idea as you risk getting banned
    # unfortunately there isn't an API endpoint for these
    return list_categories()


def identify_latest_day(category: str = "cs.AI") -> str:
    """
    Identify the latest day available on the arXiv API in the given category
    """

    base_url = "http://export.arxiv.org/api/query?"

    search_query = f"cat:{category}"
    url = f"{base_url}search_query={search_query}&start=0&max_results=1"
    url += "&sortBy=submittedDate&sortOrder=descending"

    logger.info(f"{datetime.now()}: API URL to find latest available day: {url}")

    res = requests.get(url, timeout=360)
    if not res.ok:
        latest_day = "Not Found"
        logger.error(f"{datetime.now()}: Error fetching latest day: {res.status_code}")
    else:
        # remove the time part
        latest_day = feedparser.parse(res.content)["entries"][0]["published"].split(
            "T"
        )[0]

    logger.info(f"{datetime.now()}: Latest available day: {latest_day}")

    return latest_day


def search_articles(
    query: str = "lyapunov exponents",
    sortby: str = "submittedDate",
    prefix: str = "abs",
    start: int = 0,
    max_results: int = 20,
):
    """
    Search articles on arXiv according to the query value.
    Return a markdown table with max_results articles and the following values:
    - pdf: the url to the article pdf
    - updated: the last time the article was updated
    - published: the date when the article was published
    - title: the article title
    - summary: a summary of the article's content
    If no articles are found, return "No articles found".
    Args:
        query: the query used for the search
        sortby: how to sort the results. Possible values:
            - relevance (most relevant on the top)
            - lastUpdatedDate (most recently updated on the top)
            - submittedDate (most recently submitted on top)
        prefix: the prefix used for the search. Possible values:
            - abs (abstract)
            - all (all)
            - ti (title)
            - au (author)
            - co (comment)
            - cat (category)
            - id (arXiv ID)
            - jr (journal reference)
        start: the index of the ranking where the table starts, add +20 to get the next table chunk
        max_results: the total number of articles to retrieve. The default value is 20.
    """

    time.sleep(0.5)

    search_query = f"{prefix}:{query.lower()}"
    url = f"{ARXIV_BASE_URL}search_query={search_query}&start={start}&max_results={max_results}"
    url += f"&sortBy={sortby}&sortOrder=descending"
    logger.info(f"{datetime.now()}: API URL to search articles: {url}")

    response = requests.get(url, timeout=360)
    df_articles = organise_api_response_as_dataframe(response)

    if df_articles.empty:
        return "No articles found"

    markdown = f"""
        ---{query}-{sortby}----
        {df_articles.to_markdown(index=False)}
        ------------------------
    """

    return markdown


def search_articles_by_abs(
    query: str = "lyapunov exponents",
    start: int = 0,
    max_results: int = 20,
):
    """
    Search articles on arXiv according to the query value in the text content
    of the article abstracts.
    Return a markdown table with max_results articles and the following values:
    - pdf: the url to the article pdf
    - updated: the last time the article was updated
    - published: the date when the article was published
    - title: the article title
    - summary: a summary of the article's content
    If no articles are found, return "No articles found".
    Args:
        query: the query used for the search
        start: the index of the ranking where the table starts, add +20 to get the next table chunk
        max_results: the total number of articles to retrieve. The default value is 20.
    """

    return search_articles(
        query=query,
        sortby="relevance",
        prefix="abs",
        start=start,
        max_results=max_results,
    )


def search_articles_by_title(
    query: str = "lyapunov exponents",
    start: int = 0,
    max_results: int = 20,
):
    """
    Search articles on arXiv by title.
    Return a markdown table with max_results articles and the following values:
    - pdf: the url to the article pdf
    - updated: the last time the article was updated
    - published: the date when the article was published
    - title: the article title
    - summary: a summary of the article's content
    If no articles are found, return "No articles found".
    Args:
        query: the query used for the search
        start: the index of the ranking where the table starts, add +20 to get the next table chunk
        max_results: the total number of articles to retrieve. The default value is 20.
    """

    return search_articles(
        query=query,
        sortby="relevance",
        prefix="ti",
        start=start,
        max_results=max_results,
    )


def retrieve_recent_articles(
    category: str = "cs.AI",
    latest_day: str = "2022-01-01",
):
    """
    Search articles on arXiv by category, filtering to the ones publishhed
    on the latest available day.
    Return a markdown table with articles and the following values:
    - pdf: the url to the article pdf
    - updated: the last time the article was updated
    - published: the date when the article was published
    - title: the article title
    - summary: a summary of the article's content
    If no articles are found, return "No articles found".
    Args:
        category: the category ID used for the search
        latest_day: the day of publications to filter articles by
    """

    search_query = f"cat:{category}"
    # 300 is empirical: there should never be more articles in a day for a category
    url = f"{ARXIV_BASE_URL}search_query={search_query}&start=0&max_results=300"
    url += "&sortBy=submittedDate&sortOrder=descending"
    logger.info(f"{datetime.now()}: API URL to retrieve recent articles: {url}")

    response = requests.get(url, timeout=360)
    df_articles = organise_api_response_as_dataframe(response)

    if df_articles.empty:
        return "No articles found"

    # remove time part from published and filter DF to latest day (string)
    df_articles["published"] = df_articles["published"].apply(lambda s: s.split("T")[0])
    df_articles = df_articles[df_articles["published"] == latest_day]

    return df_articles.to_markdown(index=False)


def get_article(url: str, max_attempts: int = 10) -> str:
    """
    Opens an article using its URL (PDF version) and returns its text content.
    Args:
        url: the article arXiv URL
        max_attempts: the maximum number of attempts to open the article. Default is 10.
        Do not change this parameter.
    """

    logger.info(f"{datetime.now()}: API URL to retrieve article: {url}")

    attempts = 0
    article = ""

    while attempts < max_attempts:
        try:
            res = requests.get(url, timeout=360)
            if not res.ok:
                article = "Not Found"
            else:
                bytes_stream = BytesIO(res.content)
                try:
                    with pymupdf.open(stream=bytes_stream) as doc:
                        article = chr(12).join([page.get_text() for page in doc])
                except pymupdf.FileDataError:
                    article = "Not Found"
                break
        except requests.exceptions.ConnectionError:
            logger.error(
                f"{datetime.now()}: ConnectionError exception occurred, retrying in 60 seconds..."
            )
            time.sleep(60)
            attempts += 1

    # curtail the article to 100k characters (there can be books, too long)
    article = article[:100000]

    article = f"""
        -------{url}------------
        {article}
        ------END----------------
    """

    return article
