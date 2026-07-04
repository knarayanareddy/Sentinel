import os
import sys
from dotenv import load_dotenv

# Load .env file if it exists (before validation)
load_dotenv()

REQUIRED_KEYS = ["VULTR_API_KEY", "REASONING_PRIME_MODEL",
                 "REASONING_CORE_MODEL", "REASONING_FLASH_MODEL"]


def load_and_validate():
    missing = [k for k in REQUIRED_KEYS if not os.getenv(k)]
    if missing:
        print(f"[SENTINEL] Missing required env vars: {missing}")
        sys.exit(1)

    env = os.getenv("SENTINEL_ENV", "demo")
    if env == "demo" and not os.getenv("SANDBOX_EMAIL_SINK"):
        print("[SENTINEL] FATAL: SANDBOX_EMAIL_SINK must be set in demo mode")
        sys.exit(1)

    return {
        "vultr_api_key": os.environ["VULTR_API_KEY"],
        "vultr_base_url": os.getenv("VULTR_BASE_URL", "https://api.vultrinference.com/v1"),
        "reasoning_prime": os.environ["REASONING_PRIME_MODEL"],
        "reasoning_core": os.environ["REASONING_CORE_MODEL"],
        "reasoning_flash": os.environ["REASONING_FLASH_MODEL"],
        "vultron_rerank": os.getenv("VULTRON_RERANK_MODEL", "vultr/VultronRetrieverFlash-Qwen3.5-0.8B"),
        "secondary_model": os.getenv("SECONDARY_MODEL", "deepseek-ai/DeepSeek-V4-Flash"),
        "sentinel_env": env,
        "sandbox_sink": os.getenv("SANDBOX_EMAIL_SINK", "mailhog"),
        "drift_threshold": float(os.getenv("DRIFT_THRESHOLD", "0.40")),
        "citation_threshold": float(os.getenv("CITATION_THRESHOLD", "0.60")),
        "maars_confidence_min": int(os.getenv("MAARS_CONFIDENCE_MIN", "70")),
    }


CONFIG = load_and_validate()
