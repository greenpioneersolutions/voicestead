# Voicestead — Brand Guide · "The Resonant"

The logo is a fountain-pen nib whose written line becomes a **voice waveform** — ink turning into voice at the point of contact. It's the visual form of the product's promise: *writing that sounds like you, and never invents a fact.* The pen is craft; the wave is voice. Keep those two roles distinct in every use.

---

## Logo

**The mark** = the nib + the waveform. **The lockup** = the mark + the wordmark "Voicestead" set in Fraunces.

**Files (in this bundle):**
- `voicestead-mark.svg` — full color, for **light** backgrounds.
- `voicestead-mark-reversed.svg` — for **dark** backgrounds.
- `voicestead-mark-mono.svg` — single color; uses `currentColor`, so it takes on the surrounding text color. Use where color isn't available.
- `voicestead-lockup.svg` / `voicestead-lockup-reversed.svg` — horizontal logo + wordmark (light / dark).
- `favicon.svg` — simplified mark on an ink tile for small sizes.
- `og-image.svg` — 1200×630 social card (export to PNG/JPG for `og:image`).

**Rules**
- **Clear space:** keep empty space of at least **50% of the mark's height** on all sides. For the lockup, keep at least the cap-height of the "V".
- **Minimum size:** mark ≥ **24px**. Below that, use `favicon.svg`. In the lockup, keep the "V" cap-height ≥ **14px**.
- **The pen is always ink (`#1C4066`); the wave is always azure (`#2A92D4`).** That contrast is the whole idea.
- **Don't:** recolor the pen to azure or the wave to ink · stretch, skew, or rotate · add drop shadows, bevels, or gradients to the mark · place the color mark on a busy photo (use the reversed or mono mark, or a solid scrim).

---

## Color

| Token | Hex | Role |
|---|---|---|
| Ink Pen | `#1C4066` | **Primary.** The pen. Headings and body text on light. |
| Deep Ink | `#14324F` | Darker shade for large display type / depth. |
| Voice Azure | `#2A92D4` | **Accent.** The wave. Links, primary buttons, focus, highlights. |
| Azure Bright | `#46A6E6` | Accent on dark surfaces. |
| Steel | `#7C93A8` | Muted / secondary text; hairlines on light. |
| Mist | `#EAF1F7` | Tinted surface — cards, soft sections. |
| Cloud | `#F4F8FB` | Alternate light page background. |
| Ink Night | `#0F2437` | Dark sections / footer. |
| Ice | `#DCE6EF` | Text / logo on dark. |
| White | `#FFFFFF` | Base background; text on ink buttons. |

**Signature gradient** — "ink becomes voice": `linear-gradient(90deg, #1C4066 0%, #2A92D4 100%)`. Reserve it for the waveform, primary buttons, and the occasional accent underline. Ink and azure carry the identity; the gradient is a seasoning, not the meal.

**Contrast:** Ink Pen on White and Ice on Ink Night both pass WCAG AA for body text. Use Deep Ink (not Steel) for anything that must be readable; Steel is for secondary text and hairlines only.

---

## Type

- **Display — Fraunces.** Headings, hero, and the logo wordmark. Weights 400 / 560. Track slightly tight at large sizes (−0.02em). Literary and warm; carries the "words" feeling.
- **Body / UI — Inter.** Paragraphs, navigation, buttons, labels. Weights 400 / 500 / 600. Clean and highly legible.
- **Mono — IBM Plex Mono.** Eyebrows, tags, metadata, and code. Weights 400 / 500. Uppercase with `letter-spacing: .12–.16em` for eyebrows.

Google Fonts import (also in `brand-tokens.css`):
```
https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,560;1,9..144,460&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap
```

---

## Voice & tone (for any copy the design tool writes)

Voicestead is a tool that strips the "tells" out of writing — so its own words should model that.
- Plain words, concrete nouns, short sentences. One idea per sentence.
- Active voice. Say the thing directly.
- **Ban the hype:** *revolutionary, unleash, seamless, supercharge, game-changing, effortlessly, elevate, empower, cutting-edge.*
- No em-dash-stacked crescendos, no rule-of-three flourishes for their own sake.
- **Do not change the meaning of existing product claims.** Restyle and lay out; don't rewrite what the product does.

If a line reads like marketing filler, cut it. That's the product's whole point.
