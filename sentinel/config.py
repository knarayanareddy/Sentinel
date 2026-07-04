import os
import sys
from dotenv import load_dotenv

# Load .env file if it exists (before validation)
load_dotenv()

REQUIRED_KEYS = ["VULTR_API_KEY", "VULTRON_PRIME_MODEL",
                 "VULTRON_CORE_MODEL", "VULTRON_FLASH_MODEL"]


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
        "vultron_prime": os.environ["VULTRON_PRIME_MODEL"],
        "vultron_core": os.environ["VULTRON_CORE_MODEL"],
        "vultron_flash": os.environ["VULTRON_FLASH_MODEL"],
        "secondary_model": os.getenv("SECONDARY_MODEL", "qwen2.5-32b-instruct"),
        "sentinel_env": env,
        "sandbox_sink": os.getenv("SANDBOX_EMAIL_SINK", "mailhog"),
        "drift_threshold": float(os.getenv("DRIFT_THRESHOLD", "0.40")),
        "citation_threshold": float(os.getenv("CITATION_THRESHOLD", "0.60")),
        "maars_confidence_min": int(os.getenv("MAARS_CONFIDENCE_MIN", "70")),
    }


CONFIG = load_and_validate()
