"""Plan-tier credit/search allowances and credit-pack pricing.

Ported from the standalone root-level backend/constants/global_constants.py
(planToCredits, planToSearches). That backend's tier names (FREE_TIER,
BASIC_TIER, STANDARD_TIER, PREMIUM_TIER) differ from this one's `users.plan`
ENUM ('free', 'basic', 'pro', 'enterprise') — mapped 1:1 in ascending order,
amounts unchanged.
"""
from __future__ import annotations

PLAN_CREDITS: dict[str, int] = {
    "free": 0,
    "basic": 200,
    "pro": 500,
    "enterprise": 1500,
}

PLAN_SEARCHES: dict[str, int] = {
    "free": 0,
    "basic": 750,
    "pro": 2000,
    "enterprise": 6000,
}

# credits -> price in cents, for one-off top-up purchases (Stripe Checkout
# with dynamic price_data, not tied to any pre-registered Stripe Price).
CREDIT_PACKS: dict[int, int] = {
    1000: 1000,
    6000: 5000,
    30000: 20000,
}
