# Anote AI — Product & GTM Strategy

Owner note: this document makes explicit calls rather than presenting options, because the
alternative — punting every decision back to you — defeats the point of writing it. Overturn
anything below; nothing here is final until you say so.

## 1. The honest premise

Anote cannot out-execute Anthropic or OpenAI on "better version of Claude Code." They own the
model, subsidize inference with model-margin, and ship the CLI as a loss-leader for API revenue.
A clone competing on prompt quality alone loses that fight before it starts.

The market isn't winner-take-all, though: 70%+ of engineers already run 2-4 AI coding tools
side by side (editor tool + terminal agent + completions + CI automation), and Claude Code leads
on satisfaction while Copilot leads on raw distribution — no single tool owns the workflow.
The opening is a **wedge**: something the incumbents structurally can't ship, not a better clone
of what they already ship.

## 2. The wedge: omni-channel session continuity

Claude Code, Codex, Cursor — all single-surface. The agent lives in one terminal or one editor
window. Anote already has, in this repo, a CLI, a VS Code extension, a web app, a mobile app, a
desktop app, and bot integrations for Slack/SMS/WhatsApp under one backend and one account model.
No competitor has that surface area today.

**Decision: build the primitive that makes those surfaces one product, not seven.** First
instance: an agent session started in the CLI can pause on a risky action and be
approved/denied from Slack, SMS, or mobile — without the person being at the terminal. This is
useless as a demo gimmick and genuinely useful as infrastructure: it's how a coding agent
becomes something a manager or on-call engineer can supervise from a phone, which is a workflow
Claude Code and Codex cannot offer by construction (they have no other surface to hand off to).

Everything else — vertical/compliance packaging, pricing, positioning — sits on top of this
primitive once it exists. Building it first is also the cheapest way to falsify the whole
strategy: if nobody cares about cross-surface handoff, better to find out in week one.

## 3. What ships this session vs. what needs you

**Shipped in this pass (code, not slideware):**
- `packages/backend/api_endpoints/approvals` — a pending-approval primitive (create / list /
  get / respond), the backend half of the handoff.
- Tests for it, in the existing pytest/Flask-test-client style.
- `packages/cli/src/hooks.ts` — a `requestApproval()` path so a CLI session can raise an
  approval, wait, and resume from a decision made elsewhere.
- Slack bot command to list and resolve pending approvals from `packages/bots/slack`.

**Cannot be made autonomous, and I won't pretend otherwise:** opening a bank account or
Stripe account, registering a legal entity, buying ads, cold-emailing prospects, publishing to
the App Store / Chrome Web Store (needs your developer identity), signing any contract, or
making pricing/legal commitments on your behalf. Those need your name, money, or signature.
What I can do without you: write the code, write docs, open PRs, and keep iterating — I'll flag
the moment a task needs one of the above instead of quietly skipping it.

## 4. Roadmap

**Phase 0 (this session): prove the primitive.** Approvals API + CLI hook + Slack resolution,
working end to end locally. Ship as a demo-able loop: run a CLI session, trigger an approval,
resolve it from Slack, watch the CLI resume.

**Phase 1 (weeks 1-2): make it the default coding-agent workflow.** Extend approvals to
mobile push (infra already exists in `packages/mobile`) and web. Add session-status streaming
so any surface can *watch* a running session, not just approve/deny one action. This is the
point where "Anote" stops being "a CLI" and becomes "the CLI plus a place to supervise it."

**Phase 2 (weeks 3-6): beachhead segment.** Target teams that already run agent CLIs
unattended (CI bots, overnight refactor jobs, scheduled agent runs) — they're the ones who
concretely need remote approval because nobody is at a terminal when the agent needs a
decision. This is a narrow, findable audience (teams posting about "YOLO mode" / auto-approve
agent runs), not a mass-market pitch.

**Phase 3 (weeks 6+, needs you): compliance/on-prem packaging.** Self-hosted backend, audit
log export, VPC-only deployment — the second differentiator from the original analysis, aimed
at regulated teams who can't send code to a third-party cloud at all. This phase is sales-cycle
heavy and needs a human relationship; I can build the on-prem deployment path, not run the sales
motion.

## 5. GTM shape

- **Position as "add this," not "replace Claude Code."** The multi-tool-adoption data means the
  pitch is "the supervision layer for whatever agent you already run," not a rip-and-replace.
- **Distribution starts where Anote already has users** — web/mobile install base — expanding
  into CLI usage, rather than trying to win cold CLI-market share against Claude Code/Codex
  head-on.
- **Pricing:** usage-based, not seat-based — undercuts the friction of enterprise per-seat CLI
  licensing for teams already paying for a coding agent and just adding supervision on top.
- **Content motion:** the wedge is inherently demo-able (agent pauses, phone buzzes, you tap
  approve, terminal resumes) — this is a 30-second video, not a slide deck. That's the top of
  funnel, and it's something I can help produce once the feature is real.

## 6. Metrics that matter early

- Time-to-first-approval-resolved-remotely (activation signal for the wedge itself).
- % of sessions that raise at least one remote approval (adoption of the differentiator, not
  vanity DAU).
- Approval response latency by surface (Slack vs. mobile vs. web) — tells you which surface to
  invest in next.
- Anything about model quality, token cost, or completion accuracy is explicitly *not* a
  north-star metric here — that's the incumbents' game, not the one we're playing.

## 7. What I need from you, concretely, when you're back

1. Which beachhead in Phase 2 matches who you actually know / can talk to — I can build for a
   segment, I can't pick one out of thin air with confidence.
2. Slack app credentials (or a workspace to create a test app in) to move the Slack integration
   from code to a running bot.
3. A decision on hosted vs. self-hosted default before Phase 3 — that's a pricing and infra
   commitment, not an engineering one.

Everything else in this doc, I'll keep executing against without waiting on you.
