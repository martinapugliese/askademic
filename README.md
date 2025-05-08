<p align="center"><img src="assets/logo_res.jpeg" alt="Askademic" width="150" height="150"></p>
<h1 align="center">
Askademic

![example workflow](https://github.com/martinapugliese/askademic/actions/workflows/python-package.yml/badge.svg)

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/martinapugliese/askademic)
</h1>

# What is this

_Tip: you can use [DeepWiki](https://deepwiki.com/martinapugliese/askademic) to see details and ask questions about this!_

Askademic is an AI agent, working as a CLI tool, that helps you with finding information in research papers, so long as they are on **arXiv**. It queries the arXiv API and can:
* summarise the latest papers in a category
* answer questions, searching first for relevant papers
* retrieve info about a specific paper, by link or title

You can also ask follow-up questions. And, it has an eye for things non-scientific... see below.

As for everything that uses LLM, **check your outputs** - it can make mistakes.

It uses Google Gemini 2.0 Flash. We aim to expand it to allow for multiple LLMs in the (near) future, especially open ones, but this early choice has been motivated by these factors:
* it has a free tier - we privilege cost-effectiveness over speed, which means for short conversations you should be within the quotas of the free tier
* it has a very large context window, very useful for questions where extensive searches over many papers are needed

Askademic is built on [PydanticAI](https://ai.pydantic.dev/).

# Requirements

Works with Python 3.11 and above. Not yet published on PyPI while we iron out some things to improve.

# Installation & setup

1. Clone this repo
2. `cd` into it and pip install it as `pip install .` Alternatively, you can `pip install` from the GitHub link. Or, use `uv` with `uv tool install --python python3.11 .` — this lets you choose the exact Python version for your environment, which is useful for testing or compatibility.
3. Then, you need a Gemini API key. Head to [Google AI Studio](https://aistudio.google.com/app/apikey) to generate it
4. Set the env var for it, you can use `export GEMINI_API_KEY=your-api-key` - this will only persist your API key to the session. To persist it globally you need to add it to your bash/ZSH profile.

# Run it

Run it with command `askademic` from the terminal.

# Examples of what it can do

### When you ask for a summary of latest papers

![example of summary1](assets/summary1.png)

![example of summary2](assets/summary2.png)

### When you ask questions - with and without follow-up

![example of question1](assets/question1.png)

![example of question2](assets/question2.png)

![example of question3](assets/question3_and_convo.png)

### When you ask a question or details about a specific article

![example of article1](assets/article1.png)

![example of article2](assets/article2.png)

### When you ask something non-scientific, you deserve a pun!

![example of question1](assets/pun.png)

# Roadmap and issues

Please try it and give us feedback! If you find quirks or something that is not great, you are more than welcome to open an issue in this repo, please describe the issue clearly, ideally with screenshots.

We have several ideas to develop this further, adding new capabilities and features, so stay tuned!

# Acknowledgments

Thank you to arXiv for use of its open access interoperability. This [service/ product] was not reviewed or approved by, nor does it necessarily express or reflect the policies or opinions of, arXiv.

Logo: GPT4o

# Licence

2025 - GNU General Pubic License v3
