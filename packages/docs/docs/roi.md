# ROI: What Document Q&A Is Worth

A one-page business case for AI document Q&A — with an interactive calculator, the math behind it, and sources you can cite in a procurement conversation. Use your browser's **Print → Save as PDF** on this page to produce the sales one-pager.

---

## The problem, quantified

Knowledge workers spend a large share of their day just *finding* information:

- **19% of the workweek** — roughly 1.5 hours of an 8-hour day — is spent searching for and gathering internal information, per McKinsey Global Institute's analysis of the social economy.[^1]
- IDC's widely cited knowledge-worker research puts search and information-gathering at **~2.5 hours per day** for information-intensive roles.[^2]
- At a fully loaded analyst cost of **$40/hour** (≈$80K salary), even the conservative McKinsey figure represents **~$15,000 per person per year** spent searching rather than analyzing.

AI document Q&A attacks this directly: instead of opening, scrolling, and skimming documents, the analyst asks a question and gets an answer with the source passage attached.

## Interactive ROI calculator

<div class="roi-calc">
<style>
.roi-calc { border: 1px solid var(--md-default-fg-color--lightest); border-radius: 12px; padding: 1.2rem 1.4rem; margin: 1rem 0; }
.roi-calc label { display: block; font-size: 0.75rem; font-weight: 600; margin-top: 0.8rem; }
.roi-calc input[type=range] { width: 100%; }
.roi-calc .roi-val { font-weight: 400; float: right; }
.roi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 0.8rem; margin-top: 1.2rem; }
.roi-stat { border-radius: 10px; padding: 0.8rem; background: var(--md-code-bg-color); }
.roi-stat b { display: block; font-size: 1.3rem; }
.roi-stat span { font-size: 0.7rem; }
@media print { .roi-calc input[type=range] { display: none; } }
</style>

<label>Team size <span class="roi-val" id="roi-team-val">10 people</span>
<input type="range" id="roi-team" min="1" max="200" value="10"></label>

<label>Average fully loaded salary <span class="roi-val" id="roi-salary-val">$80,000</span>
<input type="range" id="roi-salary" min="40000" max="250000" step="5000" value="80000"></label>

<label>Hours per day spent searching documents <span class="roi-val" id="roi-hours-val">1.5 h</span>
<input type="range" id="roi-hours" min="0.5" max="4" step="0.25" value="1.5"></label>

<label>Share of search time recovered with document Q&A <span class="roi-val" id="roi-recov-val">50%</span>
<input type="range" id="roi-recov" min="10" max="90" step="5" value="50"></label>

<div class="roi-grid">
  <div class="roi-stat"><b id="roi-hours-year">—</b><span>hours recovered / year</span></div>
  <div class="roi-stat"><b id="roi-per-user">—</b><span>saved / person / year</span></div>
  <div class="roi-stat"><b id="roi-total">—</b><span>saved / team / year</span></div>
</div>

<script>
(function () {
  var $ = function (id) { return document.getElementById(id); };
  var fmt = function (n) {
    return "$" + Math.round(n).toLocaleString("en-US");
  };
  function recalc() {
    var team = +$("roi-team").value;
    var salary = +$("roi-salary").value;
    var hours = +$("roi-hours").value;
    var recov = +$("roi-recov").value / 100;
    var hourly = salary / 2000; // 250 working days × 8 h
    var hoursSavedYear = hours * recov * 250;
    var perUser = hoursSavedYear * hourly;
    $("roi-team-val").textContent = team + (team === 1 ? " person" : " people");
    $("roi-salary-val").textContent = fmt(salary);
    $("roi-hours-val").textContent = hours + " h";
    $("roi-recov-val").textContent = Math.round(recov * 100) + "%";
    $("roi-hours-year").textContent = Math.round(hoursSavedYear).toLocaleString("en-US");
    $("roi-per-user").textContent = fmt(perUser);
    $("roi-total").textContent = fmt(perUser * team);
  }
  ["roi-team", "roi-salary", "roi-hours", "roi-recov"].forEach(function (id) {
    $(id).addEventListener("input", recalc);
  });
  recalc();
})();
</script>
</div>

**Default scenario:** a 10-person team at $80K average salary, spending the McKinsey-estimated 1.5 hours/day searching, recovering half of that time → **~187 hours and ~$7,500 recovered per person per year — ~$75,000 per team**. With IDC's 2.5 h/day figure the same team recovers **~$125,000 per year**.

## Illustrative scenario

!!! example "A 10-person research team (illustrative — not a named customer)"
    A research team maintains a corpus of 200+ internal documents — filings, contracts, past reports. Before document Q&A, answering a typical question ("What did we conclude about X last year?", "Which contracts contain a change-of-control clause?") meant locating candidate documents and reading until the passage surfaced: routinely **30–180 minutes per question**.

    With document Q&A, the same question takes **a few minutes**: ask, read the answer, click the citation, verify the passage. If each analyst resolves just two such questions per day and saves 45 minutes each time, the team recovers **~375 hours per month** — analyst time that goes back into analysis instead of retrieval.

    The honest caveats: answers still need verification against the cited source (that's why citations are a core feature, not garnish), scanned documents without a text layer index poorly, and time saved varies with document quality and question specificity. The calculator above lets a buyer plug in their own conservative assumptions.

## Why the assumptions are conservative

1. **We count only search time.** The calculator ignores second-order gains: faster onboarding, fewer interruptions of senior staff ("where is that clause?"), and decisions made with sources actually checked.
2. **50% recovery is modest.** For extractive questions over indexed documents, retrieval is near-instant; the residual time is verification — which the citation UX is designed to make fast.
3. **$40/hour is below market** for the legal, financial, and research analysts who use document Q&A most heavily.

## Cost side of the ledger

Plan pricing is per-seat with monthly question allowances (see the in-app billing page). At the default scenario's ~$7,500/person/year recovered, a plan costing a few hundred dollars per person per year pays back **>10×**; self-hosted deployments trade the subscription for infrastructure plus LLM API usage you meter yourself.

[^1]: McKinsey Global Institute, *The social economy: Unlocking value and productivity through social technologies* (2012) — reports 19% of the knowledge worker's week spent searching and gathering information. [mckinsey.com](https://www.mckinsey.com/industries/technology-media-and-telecommunications/our-insights/the-social-economy)
[^2]: IDC, *The Knowledge Quotient: Unlocking the Hidden Value of Information* (2014) and related IDC knowledge-worker studies — commonly cited at ~2.5 hours/day searching for information.
