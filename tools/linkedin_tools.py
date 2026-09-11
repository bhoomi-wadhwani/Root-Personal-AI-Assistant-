import os
from linkedin_api import Linkedin

_client = None


def _get_client() -> Linkedin:
    global _client
    if _client is None:
        email = os.getenv("LINKEDIN_EMAIL")
        password = os.getenv("LINKEDIN_PASSWORD")
        if not email or not password:
            raise ValueError("LINKEDIN_EMAIL and LINKEDIN_PASSWORD must be set in .env")
        _client = Linkedin(email, password)
    return _client


def search_people(keywords: str, limit: int = 5) -> list[dict]:
    api = _get_client()
    results = api.search_people(keywords, limit=limit)
    people = []
    for r in results[:limit]:
        people.append({
            "name": r.get("name", ""),
            "headline": r.get("headline", ""),
            "public_id": r.get("public_id", ""),
            "location": r.get("location", ""),
        })
    return people


def get_profile(public_id: str) -> dict:
    api = _get_client()
    p = api.get_profile(public_id)
    experience = [
        {"title": e.get("title", ""), "company": e.get("companyName", "")}
        for e in p.get("experience", [])[:3]
    ]
    return {
        "name": f"{p.get('firstName', '')} {p.get('lastName', '')}".strip(),
        "headline": p.get("headline", ""),
        "summary": (p.get("summary") or "")[:500],
        "location": p.get("geoLocationName", ""),
        "industry": p.get("industryName", ""),
        "experience": experience,
        "public_id": public_id,
        "entity_urn": p.get("entityUrn", ""),
    }


def add_connection(public_id: str, message: str = "") -> dict:
    api = _get_client()
    try:
        api.add_connection(public_id, message=message)
        return {"status": "Connection request sent successfully"}
    except Exception as e:
        return {"error": str(e)}


def send_message(recipient_public_id: str, message_text: str) -> dict:
    api = _get_client()
    try:
        profile = api.get_profile(recipient_public_id)
        entity_urn = profile.get("entityUrn", "")
        urn_id = entity_urn.split(":")[-1] if entity_urn else None
        if not urn_id:
            return {"error": "Could not resolve profile URN for this user"}
        api.send_message(message_body=message_text, recipients=[urn_id])
        return {"status": "Message sent successfully"}
    except Exception as e:
        return {"error": str(e)}


def get_my_feed(limit: int = 5) -> list[dict]:
    api = _get_client()
    try:
        posts = api.get_feed_posts(limit=limit)
        result = []
        for p in posts[:limit]:
            actor = p.get("actor") or {}
            name_obj = actor.get("name", {})
            actor_name = name_obj.get("text", "") if isinstance(name_obj, dict) else str(name_obj)

            commentary = p.get("commentary") or {}
            if isinstance(commentary, dict):
                text_obj = commentary.get("text") or {}
                content = text_obj.get("text", "") if isinstance(text_obj, dict) else str(text_obj)
            else:
                content = str(commentary)

            result.append({
                "author": actor_name or "Unknown",
                "content": content[:300] or "(no text content)",
            })
        return result
    except Exception as e:
        return [{"error": str(e)}]
