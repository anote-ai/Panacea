"""Fictional GitHub, Jira and Notion data for the demo workspace.

The demo engineer owns ``anote-demo/acme-api``, a tiny billing service. Its
history (PRs, review comments, tickets, docs) is what the demo knowledge pack is
built from, and ACME-142 is the ticket the walkthrough hands to the AI engineer.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

REPO = "anote-demo/acme-api"
LOGIN = "natan-demo"
SITE = "https://acme-demo.atlassian.net"

FILES: dict[str, str] = {
    "README.md": "# acme-api\n\nBilling service for Acme: quotes, invoices, and discounts.\n\n"
                 "Run the tests with `python -m pytest`.\n",
    "CONTRIBUTING.md": "# Contributing\n\n- Money is `Decimal`, never `float`.\n- Every change ships with a test.\n"
                       "- One change per PR.\n- Catch specific exceptions, never bare `except`.\n",
    "requirements.txt": "pytest==8.3.3\n",
    "app/__init__.py": "",
    "app/pricing.py": '''"""Seat pricing for Acme plans."""
from decimal import Decimal

SEAT_PRICE = Decimal("40.00")
VOLUME_TIERS = [(100, Decimal("0.20")), (50, Decimal("0.10"))]


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
''',
    "app/invoices.py": '''"""Invoice totals."""
from decimal import Decimal

TAX_RATES = {"US-NY": Decimal("0.08875"), "US-CA": Decimal("0.0725")}


def invoice_total(subtotal: Decimal, region: str) -> Decimal:
    rate = TAX_RATES.get(region, Decimal("0"))
    return (subtotal * (1 + rate)).quantize(Decimal("0.01"))
''',
    "tests/__init__.py": "",
    "tests/test_pricing.py": '''from decimal import Decimal

import pytest

from app.pricing import monthly_quote, volume_discount


def test_small_team_pays_list_price():
    assert monthly_quote(10) == Decimal("400.00")


def test_volume_discount_tiers():
    assert volume_discount(49) == Decimal("0")
    assert volume_discount(50) == Decimal("0.10")
    assert volume_discount(100) == Decimal("0.20")


def test_zero_seats_is_rejected():
    with pytest.raises(ValueError):
        monthly_quote(0)
''',
}

TICKET_KEY = "ACME-142"
TICKET = {
    "key": TICKET_KEY, "summary": "Annual billing: two months free when paying yearly",
    "description": ("Customers asked to pay yearly. Add an annual quote.\n\n"
                    "Acceptance criteria:\n"
                    "- annual_quote(seats) returns 10x the monthly quote (two months free)\n"
                    "- Volume discounts still apply\n"
                    "- Fewer than 1 seat raises ValueError, same as monthly\n"
                    "- Documented in the README"),
    "status": "To Do", "url": f"{SITE}/browse/{TICKET_KEY}",
}

# The pull requests the owner wrote: (number, title, body, files, days ago)
PULLS: list[tuple[int, str, str, list[str], int]] = [
    (31, "fix: round invoice totals to cents", "Totals had 4 decimals. Quantize to cents. Adds a regression test.",
     ["app/invoices.py", "tests/test_invoices.py"], 4),
    (28, "feat: volume discount tiers for 50+ seats", "10% at 50 seats, 20% at 100. Tests cover each boundary.",
     ["app/pricing.py", "tests/test_pricing.py", "README.md"], 9),
    (25, "fix: unknown tax region no longer crashes invoices", "Default to 0% and log it instead of KeyError.",
     ["app/invoices.py", "tests/test_invoices.py"], 15),
    (22, "refactor: money is Decimal everywhere", "Floats were losing cents on large invoices.",
     ["app/pricing.py", "app/invoices.py", "tests/test_pricing.py"], 22),
    (19, "feat: /health endpoint for the load balancer", "Returns build sha and db status.",
     ["app/health.py", "tests/test_health.py"], 30),
    (17, "chore: pin dependencies and add CI", "Lock versions; run pytest and ruff on every PR.",
     ["requirements.txt", ".github/workflows/ci.yml"], 36),
]

REVIEW_COMMENTS: list[tuple[int, str, str]] = [
    (33, "app/pricing.py", "Please add a test for the zero-seat case before we merge."),
    (33, "app/pricing.py", "Money should be Decimal, never float. 0.1 + 0.2 will bite us on invoices."),
    (34, "app/invoices.py", "Don't catch bare Exception here. Catch KeyError so real bugs still surface."),
    (34, "app/invoices.py", "Name this `seat_count` instead of `n` so it reads without context."),
    (35, "app/api.py", "Can we keep this PR to one change? Split the refactor into its own PR."),
    (35, "tests/test_api.py", "Missing a test for the error path."),
    (36, "app/pricing.py", "Prefer an early return over the nested ifs."),
    (36, "tests/test_pricing.py", "This test was skipped. Fix it or delete it, but don't skip it."),
]

TICKETS: list[tuple[str, str, str, str, bool, int]] = [
    (TICKET_KEY, TICKET["summary"], TICKET["description"], "To Do", False, 1),
    ("ACME-131", "Invoices show 4 decimal places", "Customers see $1,204.1250. Round to cents.", "Done", True, 5),
    ("ACME-127", "Volume discount for large teams", "Sales needs tiers at 50 and 100 seats.", "Done", True, 10),
    ("ACME-118", "Crash on unknown tax region", "KeyError when region is missing from TAX_RATES.", "Done", True, 16),
]

PAGES: list[tuple[str, str, str]] = [
    ("Engineering conventions", "eng-conventions",
     "# Engineering conventions\n- Money is Decimal, never float\n- Every change ships with a test, including the error path\n"
     "- One change per PR; refactors go in their own PR\n- Catch specific exceptions\n- Prefer early returns\n"
     "- Names say what they hold: seat_count, not n"),
    ("How I ship a feature", "how-i-ship",
     "# How I ship a feature\n1. Restate the ticket as acceptance criteria\n2. Write the failing test first\n"
     "3. Smallest change that passes\n4. Update the README if behavior changed\n5. Open the PR with the ticket key in the title"),
    ("Postmortem: double-charged invoices", "postmortem-invoices",
     "# Postmortem: double-charged invoices\nFloat rounding produced totals one cent off, and a retry charged twice.\n"
     "## What we changed\n- Decimal everywhere\n- Idempotency key on charges\n- Regression test per bug"),
]


def seed_items(now: datetime) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for number, title, body, files, days in PULLS:
        items.append({
            "provider": "github", "external_id": f"pr:{REPO}#{number}", "kind": "pull_request",
            "thread_id": f"github:{REPO}#{number}", "direction": "outbound", "author_name": LOGIN,
            "subject": title, "body": body, "channel": REPO, "occurred_at": (now - timedelta(days=days)).isoformat(),
            "meta": {"url": f"https://github.com/{REPO}/pull/{number}", "merged": True, "labels": [], "demo": True,
                     "files": [{"path": f, "status": "modified", "additions": 12, "deletions": 3} for f in files]},
        })
    for i, (number, path, body) in enumerate(REVIEW_COMMENTS):
        items.append({
            "provider": "github", "external_id": f"review:demo-{i}", "kind": "review_comment",
            "thread_id": f"github:{REPO}#{number}", "direction": "outbound", "author_name": LOGIN,
            "subject": f"Review on #{number}", "body": body, "channel": REPO,
            "occurred_at": (now - timedelta(days=3 + i)).isoformat(),
            "meta": {"url": f"https://github.com/{REPO}/pull/{number}", "path": path, "demo": True},
        })
    for key, summary, description, status, resolved, days in TICKETS:
        items.append({
            "provider": "jira", "external_id": f"ticket:{key}", "kind": "ticket", "thread_id": f"jira:{key}",
            "direction": "outbound", "author_name": "Priya Shah", "subject": f"{key}: {summary}", "body": description,
            "channel": "ACME", "occurred_at": (now - timedelta(days=days)).isoformat(),
            "meta": {"url": f"{SITE}/browse/{key}", "status": status, "type": "Story", "labels": [],
                     "resolved": resolved, "my_comments": [], "demo": True},
        })
    for i, (title, page_id, text) in enumerate(PAGES):
        items.append({
            "provider": "notion", "external_id": f"page:{page_id}", "kind": "page", "thread_id": f"notion:{page_id}",
            "direction": "outbound", "subject": title, "body": text, "channel": "notion",
            "occurred_at": (now - timedelta(days=20 + i)).isoformat(),
            "meta": {"url": f"https://www.notion.so/demo/{page_id}", "demo": True},
        })
    return items
