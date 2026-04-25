from src.extractors import extract_fields, load_rules

def test_invoice_extraction():
    text = """
    Invoice # INV-12345
    Date: 01/15/2024
    Amount Due: $1,250.00
    """

    rules = load_rules("rules/invoice_rules.yaml")
    result = extract_fields(text, rules)

    assert result["invoice_number"] == "INV-12345"
    assert result["amount_due"] == "1250.00"