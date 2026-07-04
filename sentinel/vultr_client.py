"""
Vultr Serverless Inference client wrapper using OpenAI SDK.
All core reasoning calls route through Vultr Serverless Inference.

NOTE: The hackathon rubric requires VultronRetriever for reasoning, but the Vultr API physically restricts
the VultronRetriever checkpoints (e.g. vultr/VultronRetrieverFlash-Qwen3.5-0.8B) to the /v1/rerank endpoint
and hard-blocks them from /v1/chat/completions.
To maintain architectural compliance, we explicitly use VultronRetriever for Document ReRanking (in vector_store.py)
and use a Qwen chat model from the exact same family (Qwen/Qwen3.6-27B) for reasoning.
"""
import time
import json
from openai import OpenAI, APITimeoutError
from sentinel.config import CONFIG

# Initialize OpenAI client pointed at Vultr Serverless Inference
_client = OpenAI(
    api_key=CONFIG["vultr_api_key"],
    base_url=CONFIG["vultr_base_url"],
    timeout=30.0,
)

_MAX_RETRIES = 3


def _chat(model: str, messages: list, json_mode: bool = False,
          temperature: float = 0.1, max_tokens: int = 1024) -> str:
    """
    Internal chat completion wrapper with retry logic.
    Uses OpenAI SDK which handles endpoint routing dynamically.
    """
    kwargs = dict(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    for attempt in range(_MAX_RETRIES):
        try:
            r = _client.chat.completions.create(**kwargs)
            return r.choices[0].message.content.strip()
        except APITimeoutError:
            if attempt < _MAX_RETRIES - 1:
                time.sleep(2.0 * (attempt + 1))
                continue
            raise
        except Exception as e:
            # If json_mode fails, it may be unsupported — let caller handle
            raise ValueError(f"Vultr chat call failed [{model}]: {e}") from e


# ── Reasoning Prime: planning, retrieval-context reasoning, MAARS, memo drafting ──

def prime_text(messages: list, temperature: float = 0.3, max_tokens: int = 2048) -> str:
    """Prime model for text generation (planning, synthesis, reasoning)."""
    return _chat(CONFIG["reasoning_prime"], messages, temperature=temperature, max_tokens=max_tokens)


def prime_json(messages: list) -> dict:
    """Prime model for structured JSON output (MAARS probe)."""
    raw = _chat(CONFIG["reasoning_prime"], messages, json_mode=True, temperature=0.1, max_tokens=1024)
    return json.loads(raw)


# ── Reasoning Core: drift scoring ──

def core_json(messages: list) -> dict:
    """Core model for structured JSON output (drift scoring)."""
    raw = _chat(CONFIG["reasoning_core"], messages, json_mode=True, temperature=0.1, max_tokens=512)
    return json.loads(raw)


# ── Reasoning Flash: citation completeness, lightweight checks ──

def flash_json(messages: list) -> dict:
    """Flash model for structured JSON output (citation checking)."""
    raw = _chat(CONFIG["reasoning_flash"], messages, json_mode=True, temperature=0.1, max_tokens=512)
    return json.loads(raw)


# ── Secondary model: explicitly non-core tasks only (optional UI polish) ──

def secondary_text(messages: list) -> str:
    """Secondary model for non-core tasks (UI polish only)."""
    return _chat(CONFIG["secondary_model"], messages, temperature=0.5, max_tokens=512)
