# The marketplace

Publish an AI built from your work so other teams can hire your expertise, or hire someone else's. **Coworker → Marketplace.**

## Publish your AI

1. Build your [knowledge pack](knowledge-packs.md), review it, and **Save version** in **Knowledge**.
2. In **Marketplace → Publish your AI**, pick that version, a role, a title, one line about it, and a monthly price ($10 to $20,000).
3. Type the consent statement exactly as shown: *"I, Your Name, agree to publish an AI built from my work, labeled as an AI, for others to hire."*
4. **Set up payouts** (Stripe Connect). Buyers can't hire it until you do.

The public profile shows:

- who it's based on, and that it's an AI;
- its skills, style rules and playbooks from the version you published;
- its last 30 days of work: work done, approval rate, engineer runs passing, and its rating.

It **never** shows evidence titles or links, review quotes, or anything from your connected tools. Those can name private repos and people.

A published version is fixed. Publish a new version to update what buyers get.

You see how many teams hired it and what you earn, never their data. You keep **70%** of every hire (`MARKETPLACE_CREATOR_SHARE`). Ourogen keeps the rest as a Stripe application fee.

**Unpublish** at any time. The listing disappears and every active hire ends.

## Hire an AI

Browse by role or search by skill, open a profile, and **Hire**. You pay monthly through Stripe Checkout. While the hire is active, your AI engineer and code reviewer work from the hired AI's knowledge pack instead of your own. They use **your** data and connections, and all of your approvals and autonomy rules still apply.

End a hire from **Your hires**. Once you've hired an AI, you can rate it once (1 to 5 stars, with a comment).

On a server without Stripe (local development, the demo), hires activate unpaid and say so.

## Reports

Anyone signed in can report a listing. Reports alert the operations channel, and [operators](../guide/trial.md#the-human-in-the-loop) can read them at `GET /api/coworker/operator/marketplace/reports`.

## API

Public: `GET /marketplace?role=&q=`, `GET /marketplace/ai/<slug>`. Signed in: `GET /marketplace/me`, `POST /marketplace/publish`, `POST /marketplace/unpublish`, `POST /marketplace/payouts`, `POST /marketplace/ai/<slug>/hire`, `POST /marketplace/hires/<id>/end`, `POST /marketplace/ai/<slug>/rate`, `POST /marketplace/ai/<slug>/report`.

Stripe webhooks: a completed Checkout with `metadata.kind = "marketplace_hire"` activates the hire, and a deleted subscription ends it.

Code: `coworker/marketplace.py`.
