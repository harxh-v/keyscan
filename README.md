# keyscan

![Build](https://img.shields.io/github/actions/workflow/status/harxh-v/keyscan/.github/workflows/publish.yml?branch=main)
![License](https://img.shields.io/github/license/harxh-v/keyscan)
![Stars](https://img.shields.io/github/stars/harxh-v/keyscan?style=social)
![Issues](https://img.shields.io/github/issues/harxh-v/keyscan)
![Python](https://img.shields.io/badge/python-3.x-blue)
![Last Commit](https://img.shields.io/github/last-commit/harxh-v/keyscan)

Template-driven API key validation engine  
```
┌─────────┐    ┌──────────┐    ┌──────────┐    ┌────────┐
│ Detect  │───→│ Classify │───→│ Validate │───→│ Score  │
└─────────┘    └──────────┘    └──────────┘    └────────┘
```

keyscan is a Nuclei-inspired tool built for security researchers to automatically validate exposed API keys and secrets using extensible YAML templates.

Instead of manually testing keys using scattered scripts, keyscan provides a scalable and structured workflow for secret validation.



## Why keyscan?

Finding API keys is easy.  
Validating them is time-consuming and inconsistent.

With keyscan:
- Detects and classifies keys
- Predicts possible services
- Runs validation templates automatically
- Outputs confidence-based results



## Features

| Feature | Details |
|---------|---------|
| Template-based validation | YAML templates, Easily extendable |
| Smart key classification | Regex + prefix detection (sk-, AKIA, etc.), Length + charset analysis, Entropy-based scoring |
| Async validation engine | Parallel requests using httpx |
| Confidence scoring | Returns probability-based results |
| Clean CLI output | Table output, JSON output (planned) |

---

## Installation

```bash
git clone https://github.com/harxh-v/keyscan.git
cd keyscan

pip install -e .
```

---

## Usage

### Validate a single key

```bash
keyscan -k "sk_live_123456789" -t templates/
```

### Validate keys from a file

```bash
keyscan -f keys.txt -t templates/
```

---

## Example Output

```bash
┌──────────────┬──────────┬────────────┬────────────┐
│ Key          │ Service  │ Status     │ Confidence │
├──────────────┼──────────┼────────────┼────────────┤
│ sk_live_**** │ Stripe   │ Valid      │ 0.91       │
│ AKIA****     │ AWS      │ Invalid    │ 0.76       │
└──────────────┴──────────┴────────────┴────────────┘
```

---

## Template Example

```yaml
id: stripe-key-check
service: stripe

requests:
  - method: GET
    url: https://api.stripe.com/v1/charges
    headers:
      Authorization: Bearer {{key}}

matchers:
  - type: status
    status: [200, 401]
```

---

## Project Structure

```
keyscan/
├── cli.py
├── engine/
├── classifiers/
├── templates/
├── utils/
```

---

## Security Notice

- This project does not include real API keys
- All templates use placeholders
- Do not commit live secrets

If a key is exposed:
- Revoke it immediately
- Rotate credentials

---

## Roadmap

[ ] JSON output
[ ] Burp Suite extension
[ ] GitHub Action integration
[ ] ML-based classification
[ ] Community template registry

---

## Contributing

Contributions are welcome:
- Add templates
- Improve classifiers
- Optimize performance

---

## License

Apache 2.0

## Author

Harsh Verma  

