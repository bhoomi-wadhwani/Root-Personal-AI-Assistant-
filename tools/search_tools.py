from duckduckgo_search import DDGS


def web_search(query: str, max_results: int = 5) -> list[dict]:
    results = DDGS().text(query, max_results=max_results)
    return list(results) if results else []
