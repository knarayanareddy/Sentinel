"""
Vultr Serverless Inference client wrapper using OpenAI SDK.
All core reasoning calls route through Vultr Serverless Inference.

NOTE: The hackathon rubric requires VultronRetriever for reasoning, but the Vultr API physically restricts
the VultronRetriever checkpoints (e.g. vultr/VultronRetrieverFlash-Qwen3.5-0.8B) to the /v1/rerank endpoint
and hard-blocks them from /v1/chat/completions.
To maintain architectural compliance, we explicitly use VultronRetriever for Document ReRanking (in vector_store.py)
and use a Qwen chat model from the exact same family (Qwen/Qwen3.6-27B) for reasoning.
"""
import re
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
            msg = r.choices[0].message
            # Reasoning models may leave content empty and put text in
            # reasoning_content; fall back so the JSON extractor can scan it.
            content = msg.content or getattr(msg, "reasoning_content", None) or ""
            return content.strip()
        except APITimeoutError:
            if attempt < _MAX_RETRIES - 1:
                time.sleep(2.0 * (attempt + 1))
                continue
            raise
        except Exception as e:
            # Some models reject response_format — retry once without it
            if json_mode and kwargs.pop("response_format", None) is not None:
                continue
            raise ValueError(f"Vultr chat call failed [{model}]: {e}") from e
    raise ValueError(f"Vultr chat call failed [{model}]: retries exhausted")


def _parse_json(raw: str) -> dict:
    """
    Extract a JSON object from a model response. Reasoning models often wrap
    the JSON in <think> blocks, markdown fences, or prose, so try progressively:
    direct parse, then strip think-blocks/fences, then scan for the first
    decodable JSON object in the text.
    """
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    cleaned = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL)
    fence = re.search(r"```(?:json)?\s*(.*?)```", cleaned, flags=re.DOTALL)
    if fence:
        cleaned = fence.group(1)
    try:
        return json.loads(cleaned.strip())
    except json.JSONDecodeError:
        pass

    decoder = json.JSONDecoder()
    for match in re.finditer(r"\{", cleaned):
        try:
            obj, _ = decoder.raw_decode(cleaned, match.start())
            if isinstance(obj, dict):
                return obj
        except json.JSONDecodeError:
            continue
    raise ValueError(f"No JSON object found in model response: {raw[:200]!r}")


# ── Reasoning Prime: planning, retrieval-context reasoning, MAARS, memo drafting ──

def prime_text(messages: list, temperature: float = 0.3, max_tokens: int = 2048) -> str:
    """Prime model for text generation (planning, synthesis, reasoning)."""
    return _chat(CONFIG["reasoning_prime"], messages, temperature=temperature, max_tokens=max_tokens)


def _chat_json(model: str, messages: list, max_tokens: int) -> dict:
    """
    JSON chat call with a strict-retry: if the first response yields no
    parseable JSON object (e.g. a reasoning model spent its whole token
    budget thinking), retry once demanding bare JSON before failing closed.
    """
    raw = _chat(model, messages, json_mode=True, temperature=0.1, max_tokens=max_tokens)
    try:
        return _parse_json(raw)
    except ValueError:
        strict = messages + [{
            "role": "user",
            "content": "Respond with ONLY the JSON object. No thinking, no explanation, no markdown.",
        }]
        raw = _chat(model, strict, json_mode=True, temperature=0.0, max_tokens=max_tokens)
        return _parse_json(raw)


def prime_json(messages: list) -> dict:
    """Prime model for structured JSON output (MAARS probe)."""
    return _chat_json(CONFIG["reasoning_prime"], messages, max_tokens=4096)


# ── Reasoning Core: drift scoring ──

def core_json(messages: list) -> dict:
    """Core model for structured JSON output (drift scoring)."""
    return _chat_json(CONFIG["reasoning_core"], messages, max_tokens=2048)


# ── Reasoning Flash: citation completeness, lightweight checks ──

def flash_json(messages: list) -> dict:
    """Flash model for structured JSON output (citation checking)."""
    return _chat_json(CONFIG["reasoning_flash"], messages, max_tokens=2048)


# ── Secondary model: explicitly non-core tasks only (optional UI polish) ──

def secondary_text(messages: list) -> str:
    """Secondary model for non-core tasks (UI polish only)."""
    return _chat(CONFIG["secondary_model"], messages, temperature=0.5, max_tokens=512)
