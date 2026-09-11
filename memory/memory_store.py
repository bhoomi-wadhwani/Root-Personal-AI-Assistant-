import json
from pathlib import Path

_USERS_DIR = Path(__file__).parent / "users"
_USERS_DIR.mkdir(exist_ok=True)

MAX_HISTORY = 30


def _path(user_id: int) -> Path:
    return _USERS_DIR / f"{user_id}.json"


def _load(user_id: int) -> dict:
    p = _path(user_id)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {"facts": [], "history": []}


def _save(user_id: int, data: dict) -> None:
    _path(user_id).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def add_fact(user_id: int, fact: str) -> None:
    data = _load(user_id)
    if fact not in data["facts"]:
        data["facts"].append(fact)
        _save(user_id, data)


def get_facts(user_id: int) -> list[str]:
    return _load(user_id)["facts"]


def format_facts(user_id: int) -> str:
    facts = get_facts(user_id)
    if not facts:
        return ""
    lines = "\n".join(f"- {f}" for f in facts)
    return f"Things I know about the user:\n{lines}"


def get_history(user_id: int) -> list[dict]:
    return _load(user_id)["history"]


def update_history(user_id: int, history: list[dict]) -> None:
    data = _load(user_id)
    data["history"] = history[-MAX_HISTORY:]
    _save(user_id, data)


def clear_history(user_id: int) -> None:
    data = _load(user_id)
    data["history"] = []
    _save(user_id, data)


def clear_all(user_id: int) -> None:
    p = _path(user_id)
    if p.exists():
        p.unlink()
