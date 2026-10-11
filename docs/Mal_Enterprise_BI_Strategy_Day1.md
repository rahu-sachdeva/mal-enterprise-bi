# Mal Enterprise BI — Day-1 note to Head of Data

**To:** Head of Data  
**From:** BI Lead (sole hire)  
**Date:** Day 1  
**Re:** Standing up enterprise BI while Credit, Payments, and Savings launch together

I am writing this as the working plan I would put on your desk on day one. The bank is launching three products at once, domain teams already disagree on basic definitions, Data Engineering is busy shipping pipelines, and there is no KPI dictionary or BI platform. My job is not to build every dashboard in the bank in 90 days. It is to create a trusted foundation: clear definitions, a small set of decision-ready views, and a process that stops metric chaos before it hardens into habit.

I have already built a working prototype that mirrors this plan: Executive Dashboard, Credit & Lending Dashboard, Metric Conflict view, KPI Dictionary, and a self-serve landing page. The numbers are synthetic. The design choices are the ones I would take live.

---

## Who decides when metrics conflict

This needs to be unambiguous from day one.

| Role | What they own |
|------|----------------|
| Product / Finance / Credit | Propose definitions. Keep domain-specific versions for local analysis if needed. |
| BI Lead | Run the conflict workshop, own the dictionary, document the decision, and keep executive packs on certified metrics only. I do not invent business meaning alone. |
| Finance | Strong say (effectively a veto) when the metric feeds revenue, P&L, or capital narrative. |
| **Head of Data** | **Final call on the certified enterprise definition** when domains do not agree. |
| Leadership packs (CEO / CRO / CFO) | Certified KPI IDs only, once the decision is logged. |

Short version: domains propose, BI documents and enforces, you decide the certified version. Changes later go through change control so the fight does not reopen in every weekly meeting.

---

## 1. 90-day execution plan

### How I am prioritising

If we try to cover every domain deeply in 90 days as a solo hire, we will ship a lot of charts and still not trust the numbers. I am sequencing for trust first.

1. Lock definitions and system-of-record rules before expanding the dashboard catalogue.  
2. Put money and risk ahead of engagement vanity — Credit/CBS and Finance-recognised revenue before Product login metrics.  
3. Represent Credit, Payments, and Savings on the **Executive** pack from the start, but only deep-dive **Credit** in the first 90 days.  
4. Ask Data Engineering for reusable certified marts and freshness, not one-off report extracts.

### What ships when

| Phase | Window | What I ship | Domain focus |
|-------|--------|-------------|--------------|
| Trust | Days 0–30 | KPI Dictionary v1; Metric Conflict page; **Executive Dashboard v1**; **Credit & Lending Dashboard v1**; first CBS vs warehouse recon check | Credit deep; Finance revenue as SoT; Product only for certified Active Customers; Payments and Savings as exec KPIs |
| Decisions | Days 31–60 | Weekly leadership one-pager from the Executive pack; KPI change control live; Payment Success kept on Executive (no separate Payments suite yet) | Same domains; certified-only rule enforced in leadership forums |
| Enablement | Days 61–90 | Self-serve catalogue + landing; analyst training; adoption scorecard; Year-1 backlog | Train Credit, Product, Finance; freeze new certified KPIs unless P1 |

**Days 0–30, week by week**

- Week 1: Dictionary live. Conflict view for Active Customers and Approval Rate.  
- Week 2: Executive Dashboard with eight certified KPIs — Active Customers, Approval Rate, Booking Rate, Portfolio Outstanding, Recognised Revenue, Savings AUM, Payment Success Rate, DPD30 Rate.  
- Week 3: Credit Dashboard — application → approval → booking funnel, outstanding, FPD, DPD30.  
- Week 4: Recon check on Outstanding and Booked (CBS vs warehouse). Break rate becomes a control metric, not a side conversation.

**What I need from Data Engineering (flag immediately)**

1. Daily `certified.daily_enterprise_kpis` at date × market grain.  
2. CBS loan status and outstanding as system of record for Credit balances.  
3. Finance recognised-revenue feed from GL (not Product “projected” revenue).  
4. Customer flags for open loan, open savings, active card, KYC complete, fraud block.  
5. Freshness commitment: certified marts by 08:00 GST, plus a P1 alert channel when they fail.

**Day 90 done means:** leadership quotes certified IDs only; Active Customers conflict closed in writing; Credit dashboard used in the weekly risk review; most Credit/Finance ad-hoc asks answered from certified marts rather than custom pulls.

---

## 2. KPI governance and conflict resolution

### The Active Customers problem

At launch, three teams will bring three numbers into the same meeting:

| Team | Definition they will defend | What it is really measuring |
|------|-----------------------------|-----------------------------|
| Product | App login in last 30 days | Engagement |
| Finance | Revenue-recognised transaction in last 90 days | Monetisation |
| Credit | Open loan on CBS | Credit book size |

None of these is “wrong.” They answer different questions. The problem is treating them as interchangeable when leadership asks “how many active customers do we have?”

### Certified definition I recommend (KPI-P01)

Count distinct customers with at least one **open product relationship** — active loan on CBS, or open savings account, or active card — **and** KYC complete **and** not fraud-blocked.

That definition reflects a real banking relationship across the products Mal is launching. It does not inflate with browsers who never open a product, and it does not ignore savings-only customers. Product can keep 30-day login as exploratory for engagement work. Finance can keep 90-day revenue actives for monetisation analysis. Credit can keep open-loan count for book ops. Those stay useful — they just stop being the enterprise number.

### Process (not only the answer)

| Step | Action | Owner |
|------|--------|-------|
| 1 | Log the conflict and the three formulas | BI |
| 2 | Run a 30-minute workshop; each domain brings formula + intended decision | BI facilitates; Product, Finance, Credit attend |
| 3 | Choose one certified definition for enterprise / OKR / board use | **Head of Data decides**; Finance has veto if the metric feeds revenue OKRs |
| 4 | Update the KPI Dictionary; mark the other definitions exploratory; record date and owners | BI |
| 5 | Point Executive and board packs only at the certified ID; show KPI ID on every tile | BI |
| 6 | Block silent redefinition: KPI Change Request only; quarterly dictionary audit | BI + domain owners; escalate to Head of Data |

I would use the same process for Approval Rate (Credit soft-approve vs final approve after KYC) and Revenue (Finance recognised vs Product reported).

### Decision matrix

| Question | Answer |
|----------|--------|
| Who sets the certified enterprise definition? | Head of Data, after the workshop |
| Can domains keep their own version? | Yes — exploratory only |
| Who maintains the dictionary? | BI Lead |
| What can go into CEO / CRO / CFO packs? | Certified IDs only |
| Who settles the next conflict? | Same process; Head of Data remains final |

### Governance model

**Access**

| Tier | Audience | Content |
|------|----------|---------|
| L1 | All analysts | Certified marts; Executive and Credit dashboards |
| L2 | Manager + need-to-know | Sensitive cuts / confidential segments |
| L3 | Compliance co-approve | Customer-level / PII extracts |

**Certified vs exploratory:** Certified is for executive packs, OKRs, board, and anything that could feed external or regulatory narrative. Exploratory is for local analysis and the Conflict page. Exploratory outputs should be marked “not for exec.”

**Naming:** `certified.<domain>_<entity>_<grain>`; KPI IDs like `KPI-C02`, `KPI-F01`, `KPI-P01`; markets `UAE` / `KSA`.

**Intake / SLA**

| Request | Channel | SLA |
|---------|---------|-----|
| Dataset access (L1/L2) | #bi-access or short form | 2 business days |
| Certified metric wrong / dashboard down | P1 | Under 4 business hours |
| New certified metric | Change request + workshop | Workshop within 5 business days |
| Exploratory help | Office hours | Best effort within 10 business days |

---

## 3. Self-service without metric chaos

In a regulated bank, self-serve fails when every analyst can publish a new “official” Active Customers. The model I want: people self-serve **certified data products**, not the right to redefine leadership metrics.

**Guardrails**

- Leadership and shared dashboards use certified metrics only.  
- Exploratory work stays in sandboxes.  
- Published tiles carry a KPI ID.  
- No parallel Active Customers columns in domain sheets used for leadership decks.  
- PII only through L3.

**Training**

- 90 minutes for Credit, Finance, and Product analysts: dictionary, certified vs exploratory, where to query, how to request access.  
- 30 minutes for domain leads: conflict process and what cannot go into OKRs.  
- Office hours twice a week for the first quarter.

**Adoption checks by Day 90**

| Signal | Target |
|--------|--------|
| Leadership KPIs from the certified dictionary | 100% |
| Credit/Finance ad-hoc answered from certified marts | >= 60% |
| Weekly active self-serve users | >= 15 |
| Shadow Active Customers in exec decks | 0 |
| Training completion for priority analysts | >= 80% |

If leadership packs still quote Product login actives in month three, enablement failed — regardless of how many people completed training.

---

## 4. AI-assisted reporting pilot

I would not start with open-ended natural-language query on raw tables. That creates confidence without control. The pilot I would run:

**Weekly executive narrative + anomaly alerts**, generated only from certified Executive KPIs.

| | |
|--|--|
| **In scope** | Half-page draft covering week-on-week movement on Active Customers, Approval, Booking, Outstanding, Recognised Revenue, DPD30, Payment Success. Optional Slack alert when FPD or DPD30 moves past an agreed threshold. |
| **Out of scope** | Free-form chat on PII; AI inventing or changing definitions; customer-level agents |
| **Guardrails** | Certified marts only; output labelled “AI draft — BI verified”; human BI sign-off before it reaches the CEO; prompts/outputs retained 90 days; no customer PII in prompts |
| **Success by Day 90** | Four consecutive weeks used with under 15 minutes of BI editing; at least one useful risk alert acted on; no unlabelled AI numbers in exec packs |
| **Main risks** | Plausible but wrong explanations; people trusting the draft too much; wrong table wired in. Mitigation is the allow-list plus mandatory human approve. |

This is the right first AI bet for a solo BI lead: save reporting time without reopening the definition wars.

---

## 5. Trade-offs and what I cut

### Cut from the 90-day plan

| Not in the first 90 days | Why |
|--------------------------|-----|
| Full Payments and Savings domain suites | Executive KPIs are enough for launch; Credit carries the integrity and risk load |
| Full semantic layer / open explore for every domain | Needs DE capacity and governance maturity; dictionary + certified marts first |
| Real-time streaming BI | We need a trusted daily picture more than second-level refresh |
| Marketing attribution and multi-tool sprawl | Distracts from book integrity and definition discipline |

### If I had three people instead of one

| Role | Focus |
|------|-------|
| BI Lead | Governance, executive pack, conflict facilitation |
| Analytics Engineer | Certified marts, tests, freshness with DE |
| Domain BI (Credit) | Credit deep-dives, risk packs, training |

Then I would pull forward a Payments domain dashboard and a fuller recon suite — still after the dictionary and certified-only rule are sticking.

### Biggest Year-1 adoption risk

Leadership keeps accepting domain-local numbers in the room — especially Active Customers and Approval Rate. If that continues, self-serve just scales disagreement faster.

What I need from you: from Day 30, certified-only metrics in CEO / CRO / CFO packs. I will keep the Conflict page visible until the behaviour changes.

---

## Asks this week

1. Confirm you are the final decision-maker on certified KPI conflicts.  
2. Approve KPI-P01 (Active Customers) and KPI-C02 (final Approval Rate after KYC) as v1 certified, or amend them in writing.  
3. Sponsor Data Engineering for the five mart dependencies above.  
4. Endorse certified-only for leadership packs from Day 30.

Happy to walk the prototype with you and adjust the Day-30 pack based on what leadership actually reviews each week.
