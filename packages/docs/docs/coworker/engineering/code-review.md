# AI code reviewer

Reviews pull requests (your teammates', and the AI engineer's own) against **your** standards, before a human looks.

**Coworker → Engineer → AI code reviewer**: enter a repository and PR number. In the demo, review `anote-demo/acme-api` #37, a teammate's refund helper with four problems.

## What it checks

**Every review:**

| Check | Severity |
|---|---|
| A committed secret | high |
| A skipped test | high |
| Assertions removed from a test | high |
| Catching every exception (`except:` / `except Exception`) | medium |
| Code changed with no test | medium |
| Debug output left in | low |

**When your [knowledge pack](knowledge-packs.md) has the rule** (so it applies *your* standards, not someone else's):

| Check | From the rule |
|---|---|
| Money as float | "Money is Decimal, never float." (high) |
| Unclear one-letter names | "Names say what they hold." |
| Nested ifs | "Prefer early returns." |
| Large PR | "One change per PR." |
| Docs not updated | "Update the README when behavior changes." |

With a model, it also reviews the diff for correctness bugs, security problems and missed edge cases.

Each finding has a severity, file and line, what's wrong, a suggested fix, and the pack rule it applies. Review #37 in the demo finds 5 problems with the pack and 2 without it.

## Posting the review

The review is a `github.review` action: a summary plus inline comments, as **Request changes** when there's a high-severity finding. It's posted only once you approve (or right away, if you set **Post a code review** to "Just do it" and nothing was escalated).

## When it asks a human

It escalates, and the review always waits for you, when:

- there's a high-severity finding,
- the change touches auth, payments, billing, security, crypto, secrets or permissions code, or
- the model wasn't sure.

## It learns from you

- **Dismiss** a finding to hide it from this review.
- **Don't flag this in `<repo>`** also stores a suppression, so that check never fires in that repo again (`"everywhere"` turns it off for all repos). It's the same way rejected email drafts teach the coworker.

## API

`POST /reviews` (`{"repo", "number"}`), `GET /reviews`, `GET /reviews/<id>`, `POST /reviews/<id>/findings/<finding id>/dismiss` (`{"scope": "once" | "repo" | "everywhere"}`).

Code: `coworker/engineering/review.py`.
