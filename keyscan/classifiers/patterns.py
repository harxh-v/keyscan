# Hand-curated patterns for API keys
# Based on common open-source definitions (e.g. keyhacks, trufflehog)

import re

PATTERNS = [
    {
        "service": "AWS",
        "prefix": "AKIA",
        "regex": re.compile(r"^AKIA[0-9A-Z]{16}:.*$"),
        "min_length": 40,
        "max_length": 150
    },
    {
        "service": "Stripe",
        "prefix": "sk_live_",
        "regex": re.compile(r"^sk_live_[0-9a-zA-Z]{24,99}$"),
        "min_length": 32,
        "max_length": 120
    },
    {
        "service": "Stripe Test",
        "prefix": "sk_test_",
        "regex": re.compile(r"^sk_test_[0-9a-zA-Z]{24,99}$"),
        "min_length": 32,
        "max_length": 120
    },
    {
        "service": "OpenAI",
        "prefix": "sk-",
        "regex": re.compile(r"^sk-[a-zA-Z0-9]{48}$"),
        "min_length": 51,
        "max_length": 60
    },
    {
        "service": "Slack",
        "prefix": "xox",
        "regex": re.compile(r"^xox[baprs]-[0-9]{12}-[0-9]{12}-[0-9a-zA-Z]{24}$"),
        "min_length": 40,
        "max_length": 60
    },
    {
        "service": "GitHub",
        "prefix": "ghp_",
        "regex": re.compile(r"^ghp_[0-9a-zA-Z]{36}$"),
        "min_length": 40,
        "max_length": 40
    },
    {
        "service": "SendGrid",
        "prefix": "SG.",
        "regex": re.compile(r"^SG\.[A-Za-z0-9_\-\.]{66,67}$"),
        "min_length": 69,
        "max_length": 71
    }
]
