"""One-off setup script: creates the Stripe Products/Prices for the basic
and pro subscription tiers (see packages/backend/constants.py) in whatever
Stripe account STRIPE_SECRET_KEY points at.

Enterprise is intentionally excluded — per the landing page it's
"Custom"/"Talk to us" pricing, not a self-serve Stripe Price.

**PLACEHOLDER PRICES** — $9.99/mo basic, $29.99/mo pro. Nothing in this
codebase had real dollar amounts for these tiers yet (constants.py only had
credit/message allotments). Swap _BASIC_PRICE_CENTS / _PRO_PRICE_CENTS
below for real numbers before this goes anywhere near production.

Usage — put STRIPE_SECRET_KEY in packages/backend/.env, then just:
    cd packages/backend
    python -m scripts.setup_stripe_prices

Safe to re-run: looks up existing Products by name first instead of
creating duplicates on every run.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

_BASIC_PRICE_CENTS = 999    # PLACEHOLDER — $9.99/mo
_PRO_PRICE_CENTS = 2999     # PLACEHOLDER — $29.99/mo

_TIERS = [
    ("basic", "Anote Basic", _BASIC_PRICE_CENTS),
    ("pro", "Anote Pro", _PRO_PRICE_CENTS),
]


def _find_or_create_price(stripe, plan: str, product_name: str, amount_cents: int) -> str:
    existing = stripe.Product.list(active=True, limit=100)
    product = next((p for p in existing.data if p.name == product_name), None)
    if product is None:
        product = stripe.Product.create(name=product_name, metadata={"plan": plan})
        print(f"[setup] created product '{product_name}' ({product.id})")
    else:
        print(f"[setup] found existing product '{product_name}' ({product.id})")

    prices = stripe.Price.list(product=product.id, active=True, limit=100)
    price = next(
        (p for p in prices.data if p.unit_amount == amount_cents and p.recurring
         and p.recurring.interval == "month"),
        None,
    )
    if price is None:
        price = stripe.Price.create(
            product=product.id,
            unit_amount=amount_cents,
            currency="usd",
            recurring={"interval": "month"},
            metadata={"plan": plan},
        )
        print(f"[setup] created price {price.id} (${amount_cents / 100:.2f}/mo)")
    else:
        print(f"[setup] found existing matching price {price.id} (${amount_cents / 100:.2f}/mo)")
    return price.id


def main() -> None:
    secret_key = os.environ.get("STRIPE_SECRET_KEY", "")
    if not secret_key:
        print("STRIPE_SECRET_KEY is not set.", file=sys.stderr)
        sys.exit(1)
    if secret_key.startswith("sk_live_"):
        print(
            "Refusing to run against a live Stripe key — this script is for "
            "one-time test/dev setup. Pass a sk_test_... key instead.",
            file=sys.stderr,
        )
        sys.exit(1)

    import stripe
    stripe.api_key = secret_key

    print("Creating/finding Stripe Prices for basic/pro tiers...\n")
    env_lines = []
    for plan, product_name, amount_cents in _TIERS:
        price_id = _find_or_create_price(stripe, plan, product_name, amount_cents)
        env_lines.append(f"STRIPE_PRICE_{plan.upper()}={price_id}")

    print("\nAdd these to your .env:\n")
    for line in env_lines:
        print(line)


if __name__ == "__main__":
    main()
