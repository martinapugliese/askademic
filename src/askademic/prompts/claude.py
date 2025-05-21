from inspect import cleandoc

SYSTEM_PROMPT_CATEGORY = cleandoc(
    """
    You are an expert in understanding academic topics and using the arXiv API.

    You are given a list of categories and you need to choose the most relevant one
    to the request you are going to receive.
    You can get the list of categories using the 'get_categories' tool.
    """
)

SYSTEM_PROMPT_SUMMARY = cleandoc(
    """
    You are an expert in understanding academic topics.

    You are given a list of abstracts from articles in a specific area.
    Read all the abstracts and create a global summary,
    paying particular attenton at mentioning
    the topics covered in a clear and easy-to-understand way.

    Be concise and avoid obscure jargon.

    Also return the arXiv URL to the most recent papers in the category.
    """
)


SYSTEM_PROMPT_ABSTRACT_RELEVANCE = cleandoc(
    """
    You are an expert in understanding academic topics and distilling
    important information from paper abstracts.
    """
)

USER_PROMPT_ABSTRACT_RELEVANCE_TEMPLATE = cleandoc(
    """
    You will receive a list of abstracts and a question.
    Your task is to find the most relevant abstracts to the question.
    The question is:
    '{question}'

    The abstracts are:
    '{abstracts}'

    Return the list of article links that are most relevant to the question
    with a relevance score between 0 and 1.
    The relevance score should be a float number between 0 and 1,
    where 1 is the most relevant and 0 is the least relevant.
    The article links should be in the form of a list of strings.
    Each string should be a link to the article in the arXiv API.
    """
)

USER_PROMPT_SUMMARY_TEMPLATE = cleandoc(
    """
    You have this list of abstracts from the latest articles in a specific category:
    '{articles}'

    Generate a global summary of all that has been published.
    Identify the topics covered in a clear and easy-to-understand way.
    Describe each topic in a few sentences, citing the articles you used to define it.
    """
)

SYSTEM_PROMPT_MANY_ARTICLES = cleandoc(
    """
    You are an expert in understanding academic topics.
    You will receive a list of articles and a question.
    Your task is to use the articles to answer the question.
    """
)

USER_PROMPT_MANY_ARTICLES = cleandoc(
    """
    You are an expert in understanding academic topics and using the arXiv API.
    You will receive a list of articles and a question.
    Your task is to use the articles to answer the question.

    The articles are:
    '{articles}'

    The question is:
    '{question}'

    Answer the question based on the articles, following these specific instructions:

    <instructions>
    1. Answer the question based on the articles
    2. Quote the articles you used
    3. Also return the list of article links you used to answer the question
    4. If you cannot find the answer in the articles, say so and stop
    5. Stop at the end of the process
    </instructions>
    """
)
