from __future__ import annotations

import os
from typing import Optional


def has_openai_key() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


def _client():
    from openai import OpenAI

    return OpenAI()


def model_name() -> str:
    return os.getenv("OPENAI_MODEL", "gpt-5-mini")


def pretty_bullets_uk(title: str, lines: list[str]) -> Optional[str]:
    if not has_openai_key():
        return None
    try:
        client = _client()
        resp = client.responses.create(
            model=model_name(),
            input=[
                {
                    "role": "system",
                    "content": "Поверни ТІЛЬКИ маркерований список українською. Без пояснень.",
                },
                {
                    "role": "user",
                    "content": f"{title}\n" + "\n".join(f"- {x}" for x in lines),
                },
            ],
        )
        return (getattr(resp, "output_text", "") or "").strip() or None
    except Exception:
        return None


def weekly_plan_text_uk(plan: dict) -> Optional[str]:
    if not has_openai_key():
        return None
    try:
        client = _client()
        resp = client.responses.create(
            model=model_name(),
            input=[
                {
                    "role": "system",
                    "content": "Сформуй короткий гарний план раціону українською + список покупок. Без води.",
                },
                {"role": "user", "content": f"Ось дані (JSON):\n{plan}"},
            ],
        )
        return (getattr(resp, "output_text", "") or "").strip() or None
    except Exception:
        return None
