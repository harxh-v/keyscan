# keyscan

A template-driven engine for validating exposed API keys and secrets. It classifies keys using regex, entropy, and prefixes, and maps them to HTTP templates for validation.

## Features
- Template-based validation via YAML files
- Pre-validation classification (entropy, prefix, regex matching)
- Async validation engine
- Rich output display

## Installation
```
pip install -e .
```

## Usage
Validate a single key:
```bash
keyscan -k "sk_live_123456789" -t templates/
```

Validate keys from a file:
```bash
keyscan -f keys.txt -t templates/
```
