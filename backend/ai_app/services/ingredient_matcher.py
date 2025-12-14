from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import List, Tuple, Set

BASIC_IGNORED = {
    "сіль",
    "перець",
    "вода",
    "олія",
    "масло",
    "цукор",
    "salt",
    "pepper",
    "water",
    "oil",
    "sugar",
}

UNITS = {
    "г",
    "гр",
    "кг",
    "мл",
    "л",
    "шт",
    "ст.л",
    "ч.л",
    "стл",
    "чл",
    "tbsp",
    "tsp",
    "cup",
    "cups",
}


def split_list(text: str) -> List[str]:
    parts = re.split(r"[\n,;]+", text)
    return [p.strip() for p in parts if p.strip()]


def normalize(s: str) -> str:
    s = s.lower().strip()
    s = s.replace("’", "'")
    s = re.sub(r"\(.*?\)", " ", s)
    s = re.sub(r"[\d]+([\/\.,-][\d]+)*", " ", s)
    for u in UNITS:
        s = re.sub(rf"\b{re.escape(u)}\b", " ", s)
    s = re.sub(r"[^a-zа-яіїєґ'\s-]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def tokens(s: str) -> Set[str]:
    s = normalize(s)
    return {t for t in re.split(r"[\s-]+", s) if t and t not in BASIC_IGNORED}


def similar(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def ingredient_matches_pantry(ingredient: str, pantry_items: List[str]) -> bool:
    ing = normalize(ingredient)
    if not ing:
        return False
    if ing in BASIC_IGNORED:
        return True

    for p in pantry_items:
        pn = normalize(p)
        if not pn:
            continue
        if pn in ing or ing in pn:
            return True
        if similar(ing, pn) >= 0.86:
            return True

    # токени
    it = tokens(ingredient)
    if not it:
        return False
    for p in pantry_items:
        pt = tokens(p)
        if it & pt:
            return True

    return False


def recipe_missing_ingredients(
    ingredients_text: str, pantry_items: List[str]
) -> Tuple[List[str], int, int]:
    ing_items = split_list(ingredients_text)
    missing = []
    matched = 0
    total = 0

    for item in ing_items:
        name = normalize(item)
        if not name:
            continue
        if name in BASIC_IGNORED:
            continue

        total += 1
        if ingredient_matches_pantry(item, pantry_items):
            matched += 1
        else:
            missing.append(item.strip())

    return missing, matched, total
