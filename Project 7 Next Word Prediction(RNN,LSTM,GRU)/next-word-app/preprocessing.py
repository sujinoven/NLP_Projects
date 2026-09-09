"""Keep this identical to the Colab training cleaner."""
import html
import re
import unicodedata


def clean_article(text):
    text = html.unescape(str(text))
    text = unicodedata.normalize('NFKC', text)
    text = text.translate(str.maketrans({'‘': "'", '’': "'", '“': '"', '”': '"'}))
    text = re.sub(r'https?://\S+|www\.\S+', ' ', text)
    text = re.sub(r'([a-z])([.!?])([A-Z])', r'\1\2 \3', text)
    return re.sub(r'\s+', ' ', text.lower()).strip()
