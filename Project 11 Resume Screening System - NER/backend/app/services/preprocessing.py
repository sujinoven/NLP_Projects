import re

def preprocess(text: str) -> str:
    """
    Clean and normalize input text for section splitting and embeddings.
    Preserves existing text for original extraction, while sanitizing
    symbols, bullets, tabs, and URLs.
    """
    if not isinstance(text, str):
        return ""

    # lowercase
    text = text.lower()

    # normalise bullets and tabs
    text = text.replace("\t", " ")
    text = re.sub(r"[•‣▪◦●·∙]", "-", text)

    # drop urls
    text = re.sub(r"http\S+|www\.\S+", " ", text)

    # keep letters, digits and tech symbols (c++, node.js, ci/cd, 3.5, r&d)
    text = re.sub(r"[^a-z0-9+#./\-,()&@:\n ]", " ", text)

    # tidy whitespace, but keep line breaks
    text = re.sub(r"[ ]{2,}", " ", text)
    text = "\n".join(line.strip() for line in text.split("\n"))
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()
