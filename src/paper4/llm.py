"""Guarded OpenAI client for the text/LLM directions (docs/ext/de_xuat_llm_pending.md).

Two conditions set by the project owner are enforced here, not left to callers:

1. Every request is sent with ``store=False``, so it is not kept on the OpenAI dashboard. A caller
   passing ``store`` gets an error.
2. Requests leave from a Singapore IP. Before the first request, and again whenever the last check
   is older than ``RECHECK_SECONDS``, the public egress IP is geolocated; if the country is not SG
   (for example the VPN dropped), the request is refused.

The key is read from ``.env`` at the repository root (``OPENAI_API_KEY``) and never printed.
Responses are cached on disk by a hash of (model, messages, params), so reruns cost nothing and
results are reproducible; the cache holds prompts and answers, never the key.
"""
from __future__ import annotations

import hashlib
import json
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / "results" / "llm_cache"
RECHECK_SECONDS = 120
_GEO = {"t": 0.0, "country": None}
_CLIENT = None


def _api_key() -> str:
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("OPENAI_API_KEY") and "=" in line:
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("OPENAI_API_KEY not found in .env")


def egress_country() -> str | None:
    for url in ("https://ipinfo.io/json", "https://ipapi.co/json/"):
        try:
            with urllib.request.urlopen(url, timeout=10) as r:
                d = json.load(r)
            return d.get("country") or d.get("country_code")
        except Exception:  # noqa: BLE001 - try the next service
            continue
    return None


def ensure_singapore(force: bool = False) -> None:
    if force or time.time() - _GEO["t"] > RECHECK_SECONDS or _GEO["country"] != "SG":
        _GEO["country"], _GEO["t"] = egress_country(), time.time()
    if _GEO["country"] != "SG":
        raise RuntimeError(f"egress IP country is {_GEO['country']!r}, not SG: request refused")


def _client():
    global _CLIENT
    if _CLIENT is None:
        from openai import OpenAI
        _CLIENT = OpenAI(api_key=_api_key())
    return _CLIENT


def chat(messages: list[dict], *, model: str, cache: bool = True, **params) -> str:
    """One chat completion with store=False, from a Singapore IP. Returns the message text."""
    if "store" in params:
        raise ValueError("store is fixed to False by this client")
    key = hashlib.sha256(json.dumps([model, messages, params], sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    path = CACHE / f"{key}.json"
    if cache and path.exists():
        return json.loads(path.read_text(encoding="utf-8"))["text"]
    ensure_singapore()
    resp = _client().chat.completions.create(model=model, messages=messages, store=False, **params)
    text = resp.choices[0].message.content or ""
    if cache:
        CACHE.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"model": model, "messages": messages, "params": params, "text": text,
                                    "egress_country": _GEO["country"], "store": False},
                                   ensure_ascii=False, indent=1), encoding="utf-8")
    return text


def list_models() -> list[str]:
    ensure_singapore()
    return sorted(m.id for m in _client().models.list())
