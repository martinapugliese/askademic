import requests
from bs4 import BeautifulSoup


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
