import logging
from datetime import datetime

import feedparser
import pandas as pd
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, filename="logs.txt")
logger = logging.getLogger(__name__)


def get_arxiv_categories():

    url = "https://arxiv.org/category_taxonomy"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch page, status code: {response.status_code}")

    d_categories = {}

    soup = BeautifulSoup(response.text, "html.parser")
    category_div = soup.find("div", id="category_taxonomy_list")
    categories_h4 = category_div.find_all("h4")
    for category in categories_h4:
        cat_id, cat_long = category.text.replace("(", ":").replace(")", "").split(":")
        d_categories[cat_long.strip()] = cat_id.strip()

    return d_categories


def organise_api_response_as_dataframe(response) -> pd.DataFrame:

    if not response.ok:
        logger.error(f"{datetime.now()}: No articles found")
        df_articles = pd.DataFrame()
    else:
        articles_list = feedparser.parse(response.content)["entries"]
        df_articles = pd.DataFrame(articles_list)[
            ["id", "updated", "published", "title", "summary"]
        ]
        df_articles = df_articles.rename(columns={"summary": "abstract"})
        # change ID to PDF link
        df_articles["id"] = df_articles["id"].apply(
            lambda s: s.replace("/abs/", "/pdf/")
        )

    return df_articles
