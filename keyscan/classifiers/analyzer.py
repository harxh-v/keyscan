import math
from typing import List
from keyscan.utils.models import ClassificationResult
from keyscan.classifiers.patterns import PATTERNS

def calculate_shannon_entropy(data: str) -> float:
    """Calculate the Shannon entropy of a given string to identify random keys."""
    if not data:
        return 0.0
    entropy = 0.0
    for x in set(data):
        p_x = float(data.count(x)) / len(data)
        if p_x > 0:
            entropy += - p_x * math.log(p_x, 2)
    return entropy

def analyze_key(key: str) -> List[ClassificationResult]:
    """
    Take an API key and return a list of probable services.
    Sorted by confidence descending.
    """
    results = []
    entropy = calculate_shannon_entropy(key)
    
    for pattern in PATTERNS:
        confidence = 0.0
        prefix_match = False
        regex_match = False
        
        # 1. Check length constraints
        if len(key) < pattern["min_length"] or len(key) > pattern["max_length"]:
            continue
            
        # 2. Check Prefix
        if key.startswith(pattern["prefix"]):
            confidence += 0.5
            prefix_match = True
            
        # 3. Check Regex
        if "regex" in pattern and pattern["regex"].match(key):
            confidence += 0.4
            regex_match = True
            
        # 4. Entropy Bonus for high randomness
        if entropy > 4.5:
            confidence += 0.1
            
        if confidence > 0.0:
            results.append(
                ClassificationResult(
                    service=pattern["service"],
                    confidence=min(1.0, confidence),
                    regex_match=regex_match,
                    prefix_match=prefix_match
                )
            )
            
    # Generic entropy fallback if no specific match
    if not results and entropy > 4.5 and len(key) >= 16:
        results.append(
            ClassificationResult(
                service="Unknown/Generic API Key",
                confidence=min(1.0, (entropy / 8.0) + (min(len(key), 64) / 100.0)),
                regex_match=False,
                prefix_match=False
            )
        )
        
    results.sort(key=lambda x: x.confidence, reverse=True)
    return results
