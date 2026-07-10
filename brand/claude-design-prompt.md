# Claude Design prompt — Voicestead marketing page

> This is the brief used to build the **external** marketing/landing page (a separate repo).
> It lives here so the brand rules stay in one place. This repo does **not** contain a landing page.
> Copy everything below the line into Claude Design, and upload the files from this `brand/` folder in the same message.

---

You are updating the marketing / landing page for **Voicestead**, an open-source writing skill for Claude. Its promise: *writing that sounds like you, and never invents a fact.* Apply the brand system below — "The Resonant" — across the whole page. If I've shared the existing page's code or design, restyle it in place and keep all of my copy and structure; only change the visual system, the logo, and the assets. If there's no existing page, build a clean single-page landing site from the sections listed under "Layout."

## Assets I've uploaded — use these, don't redraw the logo
- `voicestead-mark.svg` — logo mark for light backgrounds.
- `voicestead-mark-reversed.svg` — logo mark for dark backgrounds.
- `voicestead-mark-mono.svg` — one-color mark (`currentColor`) for tight spots.
- `voicestead-lockup.svg` / `voicestead-lockup-reversed.svg` — full logo + wordmark (light / dark). Use the lockup in the header and footer.
- `favicon.svg` — generate the favicon set from this (16, 32, 48, 180 apple-touch, 512) plus `favicon.ico`.
- `og-image.svg` — export to a 1200×630 PNG and wire it up as `og:image` / `twitter:image`.
- `voicestead-brand.md` and `brand-tokens.css` — the full spec and ready CSS variables. Import the tokens.

The mark is a fountain-pen nib whose written line becomes a voice waveform: the pen is craft, the wave is voice. **Never** recolor the pen to azure or the wave to ink — that contrast is the identity.

## Color (from brand-tokens.css)
- Ink Pen `#1C4066` (primary), Deep Ink `#14324F`, Voice Azure `#2A92D4` (accent), Azure Bright `#46A6E6` (on dark), Steel `#7C93A8` (muted), Mist `#EAF1F7`, Cloud `#F4F8FB`, Ink Night `#0F2437` (dark sections), Ice `#DCE6EF` (text on dark), White `#FFFFFF`.
- Signature gradient, "ink becomes voice": `linear-gradient(90deg,#1C4066,#2A92D4)`. Use it only for the hero accent, primary buttons, and the occasional underline. Ink + azure do the heavy lifting; the gradient is a seasoning.

## Type
- Headings + logo wordmark: **Fraunces** (weights 400/560, tracking −0.02em on big sizes).
- Body + UI: **Inter** (400/500/600).
- Eyebrows, tags, metadata, code: **IBM Plex Mono** (uppercase, `letter-spacing:.14em`).

## Layout (build these, or map them onto my existing sections)
1. **Header** — the light lockup, minimal nav, a text link to the GitHub repo, and a primary "Get started" button in the voice gradient.
2. **Hero** — a mono eyebrow ("Open-source Claude writing skill"), a large Fraunces headline, one plain sub-line, and two CTAs (primary gradient + a quiet secondary). Add one restrained brand touch: a thin animated waveform (the mark's wave motif) that **draws in once** on load. Respect `prefers-reduced-motion`.
3. **What it does** — a short row of value points. If I've given you my copy, use it verbatim.
4. **The four modes** — Draft, Improve, Review, Extract, as four cards on Mist surfaces with mono labels.
5. **Why it's trustworthy** — the anti-slop / "never invents a fact" angle and the testing/eval harness, told plainly.
6. **Get started / install** — a code block (IBM Plex Mono) and a link to the repo.
7. **Footer** — Ink Night background, the reversed lockup, links, and a one-line sign-off.

## Rules
- **Do not rewrite or embellish my product claims.** Restyle and lay out only. Any microcopy you must add should be plain and concrete — no hype words (revolutionary, unleash, seamless, supercharge, effortlessly). This is a writing tool; the page should read like one.
- Fully responsive; looks right down to a 360px-wide phone.
- Meet WCAG AA contrast. Use Deep Ink or Ink Pen for anything that must be readable (Steel is for secondary text only). Visible keyboard focus rings in Voice Azure.
- Keep motion subtle and single-shot; nothing looping or distracting.
- Set the favicon and OG tags from the uploaded assets.

Start by showing me the hero, then the full page.
