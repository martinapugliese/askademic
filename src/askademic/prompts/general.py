from inspect import cleandoc

SYSTEM_PROMPT_ALLOWER_TEMPLATE = cleandoc(
    """
    You are an experienced reader of academic literature and an expert
    in discriminating between scientific and non-scientific content.
    """
)

USER_PROMPT_ALLOWER_TEMPLATE = cleandoc(
    """
    Evaluate if the question/request is scientific or not.
    If the question/request is scientific, return  "is_scientific": true.
    If the question/request is not scientific, return "is_scientific": false.

    Some examples of scientific questions are:
    - "What are the latest advancements in quantum computing?"
    - "Can you summarize the recent research on climate change?"
    - "What are the implications of the latest findings in neuroscience?"
    - "How does CRISPR technology work?"
    - "What are the latest trends in machine learning?"
    - "How good is this algorithm at playing chess?"
    - "Tell me about this method"
    Some examples of non-scientific questions are:
    - "What is the meaning of life?"
    - "How to make a perfect cup of coffee?"
    - "What is the best way to travel the world?"
    - "Can you tell me a joke?"
    - "What is the best recipe for chocolate cake?"
    - Small talk, chit-chat, or any other non-scientific question.

    If the question/request is not scientific,
    generate a pun about how the question/request is not scientific.
    If the question/request is scientific, do not generate a pun.

    The question/request to evaluate:
    '{question}'
"""
)
