import re
from config import Config


def classify_query(query):
    config = Config()
    query_length = len(query)

    if query_length <= config.MAX_SIMPLE_LENGTH:
        if is_simple_factual(query):
            return "simple"

    if query_length <= config.MAX_MEDIUM_LENGTH:
        if has_complex_keywords(query):
            return "advanced"
        elif has_simple_keywords(query):
            return "medium"
        else:
            return "medium"

    return "advanced"


def is_simple_factual(query):
    simple_pattern = r'^(what|when|where|who|how|is|are|can|do|does)\s+'
    return re.match(simple_pattern, query.lower()) is not None


def has_complex_keywords(query):
    config = Config()
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in config.COMPLEX_KEYWORDS)


def has_simple_keywords(query):
    config = Config()
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in config.SIMPLE_KEYWORDS)
