import re


def remove_references_section(text: str) -> str:
    """
    Removes references/bibliography section (common in research papers)
    """
    patterns = [
        r"references\s.*", 
        r"bibliography\s.*"
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            return text[:match.start()]

    return text


def remove_citations(text: str) -> str:
    """
    Removes inline citations like:
    [1], [12], (Smith et al., 2020)
    """
    # [1], [12]
    text = re.sub(r"\[\d+\]", "", text)

    # (Author, 2020)
    text = re.sub(r"\([A-Za-z\s]+,\s*\d{4}\)", "", text)

    return text


def normalize_whitespace(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def remove_urls(text: str) -> str:
    return re.sub(r"http\S+|www\S+", "", text)