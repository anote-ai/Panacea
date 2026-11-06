"""Scripted demo work for the fictional acme-api repo, so the AI engineer and the
code reviewer can be tried with no API keys. With a model, nothing here is used."""
from __future__ import annotations

from typing import Any

# What the demo engineer writes for ACME-142 (annual billing), node by node.
DEMO_SOLUTION: dict[str, list[dict[str, str]]] = {
    "impl": [{"path": "app/pricing.py", "content": '''"""Seat pricing for Acme plans."""
from decimal import Decimal

SEAT_PRICE = Decimal("40.00")
VOLUME_TIERS = [(100, Decimal("0.20")), (50, Decimal("0.10"))]
ANNUAL_MONTHS_BILLED = 10  # pay yearly, get two months free


def volume_discount(seat_count: int) -> Decimal:
    """Fraction off the list price for large teams."""
    for minimum, discount in VOLUME_TIERS:
        if seat_count >= minimum:
            return discount
    return Decimal("0")


def monthly_quote(seat_count: int) -> Decimal:
    """Monthly price for ``seat_count`` seats, after volume discounts."""
    if seat_count < 1:
        raise ValueError("seat_count must be at least 1")
    gross = SEAT_PRICE * seat_count
    return (gross * (1 - volume_discount(seat_count))).quantize(Decimal("0.01"))


def annual_quote(seat_count: int) -> Decimal:
    """Yearly price: ten months of the monthly quote, so two months are free."""
    return (monthly_quote(seat_count) * ANNUAL_MONTHS_BILLED).quantize(Decimal("0.01"))
'''}],
    "test": [{"path": "tests/test_annual.py", "content": '''from decimal import Decimal

import pytest

from app.pricing import annual_quote, monthly_quote


def test_annual_is_ten_months():
    assert annual_quote(10) == monthly_quote(10) * 10 == Decimal("4000.00")


def test_annual_keeps_volume_discount():
    assert annual_quote(50) == Decimal("18000.00")


def test_annual_rejects_zero_seats():
    with pytest.raises(ValueError):
        annual_quote(0)
'''}],
    "docs": [{"path": "README.md", "content": "# acme-api\n\nBilling service for Acme: quotes, invoices, and discounts.\n\n"
                                         "## Annual billing\n\n`annual_quote(seats)` charges ten months of the monthly "
                                         "quote (two months free). Volume discounts still apply.\n\n"
                                         "Run the tests with `python -m pytest`.\n"}],
}

# Hidden tests the eval suite runs against the engineer's output (never shown to it).
DEMO_HIDDEN_TESTS = '''from decimal import Decimal

import pytest

from app.pricing import annual_quote


def test_hidden_annual_large_team():
    assert annual_quote(100) == Decimal("32000.00")


def test_hidden_annual_negative():
    with pytest.raises(ValueError):
        annual_quote(-3)
'''

# A teammate's pull request (#37) for the reviewer to look at: float money, a bare
# except, a skipped test, and no test for the new path.
DEMO_REVIEW_PATCH: list[dict[str, Any]] = [
    {"path": "app/refunds.py", "status": "added", "additions": 14, "deletions": 0, "patch": '''@@ -0,0 +1,14 @@
+"""Partial refunds."""
+from app.invoices import invoice_total
+
+
+def refund_amount(subtotal, region, fraction):
+    try:
+        total = float(invoice_total(subtotal, region))
+    except Exception:
+        return 0
+    if fraction > 0:
+        if fraction <= 1:
+            return round(total * fraction, 2)
+    return 0
+'''},
    {"path": "tests/test_pricing.py", "status": "modified", "additions": 1, "deletions": 0, "patch": '''@@ -14,6 +14,7 @@ def test_volume_discount_tiers():
     assert volume_discount(100) == Decimal("0.20")


+@pytest.mark.skip(reason="flaky")
 def test_zero_seats_is_rejected():
     with pytest.raises(ValueError):
         monthly_quote(0)
'''},
]
