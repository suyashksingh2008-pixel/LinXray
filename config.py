from pathlib import Path
DATABASE_FILE='scan_history.db'

max_redirects=10
max_actions=10
max_scan_depth=2
scan_timeout=2
action_wait_time=1500
ALLOWED_SCHEMES = ["http", "https"]
DANGEROUS_WORDS = [
"buy", "pay", "purchase", "checkout", "delete",
"remove", "submit", "confirm", "transfer",
"upload", "download", "logout", "sign out"
]


