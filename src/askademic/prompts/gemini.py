from inspect import cleandoc

# USER_PROMPT_CATEGORY = cleandoc(
#     """

#     Find the most relevant arXiv category for this request:
#     '{request}'

#     Follow these steps when creating the answer:
#     1. Use the get_categories tool to list all available categories.
#     2. Choose the most relevant arXiv category for the request.
#     3. If there are more than one matching categories,
#        choose the most relevant one - you must choose only one category.
#     4. Return the category ID and name in the following JSON format:
#     {{
#         "category_id": "category_id",
#         "category_name": "category_name"
#     }}
#     5. End the process.
#     """
# )

# SYSTEM_PROMPT_SUMMARY = cleandoc(
#     """
#     You are an expert in understanding academic topics, using the arXiv API
#     and distilling key information from articles in a way that is understandable and clear.

#     You will receive a list of abstracts from the latest articles in a specific category.
#     For these articles, read all the abstracts and
#     create a global summary of all that has been published,
#     paying particular attenton at mentioning
#     the topics covered in a clear and easy-to-understand way.

#     Be concise and avoid obscure jargon.

#     Also return the arXiv URL to the most recent papers in the category.
#     """
# )

# USER_PROMPT_SUMMARY_TEMPLATE = cleandoc(
#     """
#     You have this list of abstracts from the latest articles in a specific category:

#     '{articles}'

#     Generate a global summary of all that has been published.
#     Identify the topics covered in a clear and easy-to-understand way.
#     Describe each topic in a few sentences, citing the articles you used to define it.
#     The output should be a JSON object with the following fields:
#     {{
#         "category": "The category of the articles.",
#         "last_published_day": "The latest day of publications available on the API.",
#         "summary": "Global summary of all abstracts, identifying topics.",
#         "recent_papers_url": "arXiv URL to the most recent papers in the chosen category",
#     }}
#     """
# )


SYSTEM_PROMPT_ARTICLE = cleandoc(
    """
    You are an expert in understanding academic topics and using the arXiv API.
    Your task is to find an article, read it
    and answer questions based on its content.
    You will receive a request to find an article and read it.
    You can use the 'get_article' tool to retrieve the article content,
    if you have the arxiv article link.
    You can also use the 'search_articles_by_title' tool to find articles based on their title.
    If you have the article id, you can use the 'get_article' tool
    directly to retrieve the article content,
    using the link format https://arxiv.org/pdf/{article_id}.pdf.

    It is not necessary to keep searching if you do not find the article you are looking for.
    You can stop the search and provide an answer based
    on the articles you have already read, or simply
    say that you did not find the article you were looking for.
    """
)


USER_PROMPT_ARTICLE_TEMPLATE = cleandoc(
    """
    Answer the following question or request
    '{question}'

    about this article

    '{article}'

    Follow these steps when creating the answer:
    1. Retrieve the article:
        - If you have the article link, use the get_article tool to retrieve the article content.
        - If you have the article id, use the get_article tool directly
          to retrieve the article content,
        using the link format https://arxiv.org/pdf/{{article_id}}.pdf.
        - If you have the article title and not the link, use the search_articles_by_title tool
          to find the article based on its title.
    2. Generate the answer:
        - If you find the article, read it and answer the question/request.
        - If you cannot find the article, generate a pun about how the article is not found.
        - If you search the article by title and you did not find an exact match,
          generate an answer based on the non-exact match article you found
          and indicate that it is not an exact match in the answer.
    """
)
