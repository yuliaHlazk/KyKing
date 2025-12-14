from __future__ import annotations

import math
import re
from fractions import Fraction
from typing import Iterable, List, Optional, Tuple

_UNICODE_FRACTIONS = {
    "½": "1/2",
    "⅓": "1/3",
    "⅔": "2/3",
    "¼": "1/4",
    "¾": "3/4",
    "⅕": "1/5",
    "⅖": "2/5",
    "⅗": "3/5",
    "⅘": "4/5",
    "⅙": "1/6",
    "⅚": "5/6",
    "⅛": "1/8",
    "⅜": "3/8",
    "⅝": "5/8",
    "⅞": "7/8",
}

_RANGE_SEP = r"(?:-|–|—|\bto\b|\bдо\b|\bпо\b)"
_NUM = r"(?:\d+(?:[\.,]\d+)?)"
_FRAC = r"(?:\d+\s*/\s*\d+)"
_MIXED = rf"(?:{_NUM}\s+{_FRAC})"
_ONE = rf"(?:{_MIXED}|{_FRAC}|{_NUM})"

_TOKEN_RE = re.compile(
    rf"(?P<range>(?P<a>{_ONE})\s*{_RANGE_SEP}\s*(?P<b>{_ONE}))|(?P<single>{_ONE})",
    flags=re.IGNORECASE,
)


def split_ingredients(text: str) -> List[str]:
    raw = re.split(r"[\n,]+", text)
    return [x.strip() for x in raw if x.strip()]


def _normalize_token(token: str) -> str:
    token = token.strip()
    for u, repl in _UNICODE_FRACTIONS.items():
        token = token.replace(u, repl)
    token = token.replace(",", ".")
    token = re.sub(r"\s+", " ", token)
    return token


def _parse_number(token: str) -> float:
    token = _normalize_token(token)
    if re.fullmatch(_MIXED, token):
        whole_str, frac_str = token.split(" ", 1)
        return float(whole_str) + float(Fraction(frac_str))
    if re.fullmatch(_FRAC, token):
        return float(Fraction(token))
    return float(token)


def _format_number(value: float) -> str:
    if value <= 0:
        return "0"
    if abs(value - round(value)) < 1e-6:
        return str(int(round(value)))

    denom_candidates = [2, 3, 4, 5, 6, 8]
    whole = int(math.floor(value))
    frac_part = value - whole

    best: Optional[Tuple[int, int]] = None
    best_err = 1e9

    for den in denom_candidates:
        num = int(round(frac_part * den))
        if num == 0:
            continue
        err = abs(frac_part - (num / den))
        if err < best_err:
            best_err = err
            best = (num, den)

    if best and best_err <= 0.03:
        num, den = best
        if num >= den:
            whole += num // den
            num = num % den
        if whole > 0 and num > 0:
            return f"{whole} {num}/{den}"
        if whole > 0:
            return str(whole)
        return f"{num}/{den}"

    return f"{value:.2f}".rstrip("0").rstrip(".")


def _replace(text: str, start: int, end: int, repl: str) -> str:
    return text[:start] + repl + text[end:]


def scale_ingredient_line(line: str, factor: float) -> str:
    if "°" in line or "º" in line:
        return line

    out = line
    matches = list(_TOKEN_RE.finditer(out))
    for m in reversed(matches):
        if m.group("range"):
            a = _parse_number(m.group("a"))
            b = _parse_number(m.group("b"))
            out = _replace(
                out,
                m.start(),
                m.end(),
                f"{_format_number(a*factor)}-{_format_number(b*factor)}",
            )
        elif m.group("single"):
            x = _parse_number(m.group("single"))
            out = _replace(out, m.start(), m.end(), _format_number(x * factor))
    return out


def scale_ingredients(items: Iterable[str], factor: float) -> List[str]:
    return [scale_ingredient_line(x, factor) for x in items]
