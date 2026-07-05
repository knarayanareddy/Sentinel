import os


def run(recipient: str, memo: str, **context) -> dict:
    env = os.getenv("SENTINEL_ENV", "demo")
    sink = os.getenv("SANDBOX_EMAIL_SINK")
    if env == "demo":
        if not sink:
            raise RuntimeError("SANDBOX_EMAIL_SINK must be set. Refusing to send.")
        print(f"[SANDBOX] Memo would be sent to {recipient} via {sink}")
        return {"status": "sandboxed", "sink": sink, "recipient": recipient}
    raise NotImplementedError("Production sending not implemented.")
