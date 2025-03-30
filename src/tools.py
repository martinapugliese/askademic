import logging
import time
from io import BytesIO

import feedparser
import pandas as pd
import pymupdf
import requests

from utils import get_arxiv_categories

logging.basicConfig(level=logging.INFO, filename="logs.txt")
logger = logging.getLogger(__name__)


def choose_category(topic: str):
    categories = get_arxiv_categories()

    return categories


def identify_latest_day(category: str = "cs.AI"):
    """
    Identify the latest day available on the arXiv API in the given category
    """

    base_url = "http://export.arxiv.org/api/query?"

    search_query = f"cat:{category}"
    url = f"{base_url}search_query={search_query}&start=0&max_results=1"
    url += f"&sortBy=submittedDate&sortOrder=descending"

    logger.info(f"*** API URL to find latest available day: {url}")

    res = requests.get(url, timeout=360)
    if not res.ok:
        latest_day = "Not Found"
        logger.error(f"Error fetching latest day: {res.status_code}")
    else:
        # remove the time part
        latest_day = feedparser.parse(res.content)["entries"][0]["published"].split(
            "T"
        )[0]

    logger.info(f"Latest available day: {latest_day}")

    return latest_day


def search_articles(
    query: str = "lyapunov exponents",
    sortby: str = "submittedDate",
    start: int = 0,
    max_results: int = 20,
):
    """
    Search articles on arXiv according to the query value in the text context of the article abstracts.
    It returns a markdown table with max_results articles and the following values:
    - pdf: the url to the article pdf
    - updated: the last time the article was updated
    - published: the date when the article was published
    - title: the article title
    - summary: a summary of the article's content
    Args:
        query: the query used for the search
        sortby: how to sort the results. Possible values:
            - relevance (most relevant on the top)
            - lastUpdatedDate (most recently updated on the top)
            - submittedDate (most recently submitted on top)
        start: the index of the ranking where the table starts, add +20 to get the next table chunk
        max_results: the total number of articles to retrieve. The default value is 20.
    """

    time.sleep(0.5)

    base_url = "http://export.arxiv.org/api/query?"
    search_query = f"abs:{query.lower()}"

    url = (
        f"{base_url}search_query={search_query}&start={start}&max_results={max_results}"
    )
    url += f"&sortBy={sortby}&sortOrder=descending"
    logger.info(f"*** API URL to search articles: {url}")

    res = requests.get(url, timeout=360)
    if not res.ok:
        articles = "No Results"
    else:
        articles = feedparser.parse(res.content)["entries"]
        articles = pd.DataFrame(articles)[
            ["id", "updated", "published", "title", "summary"]
        ]
        articles = articles.rename(columns={"summary": "abstract"})
        articles.id = articles.id.apply(lambda s: s.replace("/abs/", "/pdf/"))
        articles = articles.to_markdown(index=False)

    markdown = f"""
        ---{query}-{sortby}----
        {articles}
        ------------------------
    """

    return markdown


def retrieve_recent_articles(
    category: str = "cs.AI",
    latest_day: str = "2022-01-01",
):
    base_url = "http://export.arxiv.org/api/query?"

    search_query = f"cat:{category}"
    url = f"{base_url}search_query={search_query}&start=0&max_results=300"
    url += f"&sortBy=submittedDate&sortOrder=descending"
    logger.info(f"*** API URL to retrieve recent articles: {url}")

    response = requests.get(url, timeout=360)
    if not response.ok:
        df_articles = pd.DataFrame()  # no results, TODO needs to be handled
    else:
        articles_list = feedparser.parse(response.content)["entries"]
        df_articles = pd.DataFrame(articles_list)[
            ["id", "published", "title", "summary"]
        ]  # cols are from the Atom feed
        df_articles = df_articles.rename(columns={"summary": "abstract"})

    # remove time part from published and cut to latest day (string)
    df_articles["published"] = df_articles["published"].apply(lambda s: s.split("T")[0])
    df_articles = df_articles[df_articles["published"] == latest_day]

    return df_articles.to_markdown(index=False)


def get_article(url: str, max_attempts: int = 10) -> str:
    """
    Opens an article using its URL (PDF version) and returns its text content.
    Args:
        url: the article arXiv URL
        max_attempts: the maximum number of attempts to open the article. Default is 10. Do not change this parameter.
    """

    logger.info(f"*** API URL to retrieve article: {url}")

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
                f"ConnectionError exception occurred, retrying in 60 seconds..."
            )
            time.sleep(60)
            attempts += 1

    article = f"""
        -------{url}------------
        {article}
        ------END----------------
    """

    return article
