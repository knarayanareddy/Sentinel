# SENTINEL — Product Brief

SENTINEL is an enterprise document agent, reasoning via VultronRetriever
models on Vultr Serverless Inference, with a built-in oversight gate.
It helps finance/compliance teams ensure that autonomous agents don't take
irreversible actions (like sending regulatory escalation memos) without
full evidentiary backing and explicit human authorisation.

Primary users: CFOs, compliance officers, risk managers.
Core action: Approve or Abort a frozen agent action in under 10 seconds,
with full signal transparency including which VultronRetriever model
produced each signal.

What the UI must communicate:
1. The agent is retrieving and reasoning over real documents (multi-pass visible)
2. Something important happened (freeze alert unmissable)
3. Why (three signals, each attributed to a specific VultronRetriever model)
4. What evidence exists (citations, retrieval scores)
5. What the operator decided, with a tamper-evident hash
