from inspect import cleandoc

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
