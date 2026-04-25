import re
import yaml
from typing import Dict, Any

from dateutil import parser as date_parser


# ----------- LOAD YAML RULES -----------

def load_rules(path: str) -> Dict[str, Any]:
    with open(path, "r") as f:
        return yaml.safe_load(f)


# ----------- NORMALIZATION HELPERS -----------

def normalize_date(value: str) -> str:
    try:
        dt = date_parser.parse(value)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return value


def normalize_amount(value: str) -> str:
    try:
        return value.replace(",", "")
    except Exception:
        return value


# ----------- CORE EXTRACTION FUNCTION -----------

def extract_fields(text: str, rules: Dict[str, Any]) -> Dict[str, Any]:
    results = {}

    for field, config in rules.items():
        patterns = config.get("patterns", [])
        value = None

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                value = match.group(1)
                break

        # Apply normalization
        if value:
            if field == "invoice_date":
                value = normalize_date(value)
            elif field == "amount_due":
                value = normalize_amount(value)

        results[field] = value

    return results