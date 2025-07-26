# scraper/description_cleaner.py

import re
from textwrap import wrap

def clean_html_text(text: str) -> str:
    """
    Cleans up raw job description HTML/text:
    - Removes excessive whitespace
    - Flattens line breaks and tabs
    """
    text = re.sub(r'\s+', ' ', text)  # collapse multiple spaces
    text = re.sub(r'[\r\n\t]', ' ', text)  # remove newlines/tabs
    return text.strip()

def chunk_text(text: str, max_tokens: int = 1000) -> list:
    """
    Splits text into smaller chunks for LLMs (approx. 4 chars per token).
    Example: 1000 tokens ≈ 4000 characters
    """
    chunk_size = max_tokens * 4
    return wrap(text, chunk_size)
