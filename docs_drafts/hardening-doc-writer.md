Good. Then the answer is **not “add more agents”** — it is **tighten the editorial contract**.

Right now your system is *correct*.
To make it **publishable**, you need to move from *structural correctness* to *editorial sharpness*.

Below is a **concrete, finite plan**. No philosophy.

---

## What is missing for “publishable”

A publishable article needs **four things simultaneously**:

1. **A clear thesis** (one sentence you could quote)
2. **Narrative progression** (each section advances, not restates)
3. **Authorial voice** (someone is clearly thinking)
4. **Controlled personality** (lightness without flippancy)

Your system currently guarantees:

* structure
* coverage
* correctness

It does **not yet guarantee**:

* thesis sharpness
* non-repetition
* voice consistency

That’s normal.

---

## The key insight (important)

> **Publishability is not a writer problem.
> It is a planning problem.**

Your writer is doing what it’s told.

So the fix is **upstream**.

---

## Step 1 — Enforce a thesis (non-negotiable)

Add this **hard requirement** to the planner prompt:

> “The document must have a single explicit thesis that is stated in the introduction and revisited (not repeated) in the conclusion.”

Why:

* Forces coherence
* Prevents section drift
* Gives critics something to enforce

Without a thesis, you get “well-written mush”.

---

## Step 2 — Make sections advance, not describe

Add this planner constraint:

> “Each section must introduce at least one new idea not present in previous sections.”

This alone will remove ~50% of the repetition you’re seeing.

This is *editorial causality*.

---

## Step 3 — Add **one** controlled meta signal

Do **not** sprinkle jokes randomly.

Instead, specify:

> “Include 1–2 dry, self-aware remarks that acknowledge the article is produced by an agentic system.”

This keeps it:

* professional
* intentional
* memorable

Example (tone-wise, not literal):

> “At this point, the structure exists not because I chose it, but because the planner insisted.”

That’s enough.

---

## Step 4 — Tighten the critic (lightly)

Add one **editorial critic check**:

Reject if:

* sections restate the same idea using different words
* tone is uniformly neutral throughout
* no sentence expresses uncertainty, tension, or judgment

This is not about style — it’s about **intellectual honesty**.

---

## Step 5 — One more pass, then stop

Do **not** iterate endlessly.

Your loop should be:

1. Generate article
2. Ask: *“Would I read this voluntarily?”*
3. If no → fix **one** upstream constraint
4. Repeat once

If it’s still not publishable after that, the prompt is wrong — not the system.

---

## What success will look like

You’ll know you’re there when:

* you disagree with parts of the article
* you feel slightly exposed by it
* it has an opinion you didn’t explicitly encode
* but you can trace *why* it emerged

That’s publishable.

---

## Final anchor (keep this)

> **Structure makes text possible.
> Editorial constraints make it worth reading.**

You’re one tightening pass away — not ten.
