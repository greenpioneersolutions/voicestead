<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="voicestead-lockup-reversed.svg">
    <img src="voicestead-lockup.svg" alt="Voicestead" width="360">
  </picture>
</p>

# Brand kit — "The Resonant"

Everything needed to represent Voicestead consistently: the logo, the color and type system, and the social card. This folder is **not shipped** in the `.skill` package — it dresses the repo and the marketing site, not the runtime skill.

The mark is a fountain-pen nib whose written line becomes a **voice waveform** — ink turning into voice. The pen is always ink (`#1C4066`); the wave is always azure (`#2A92D4`). That contrast is the identity; never swap the two.

## What's here

| File | Use |
|---|---|
| [`voicestead-mark.svg`](voicestead-mark.svg) | Mark only — light backgrounds. |
| [`voicestead-mark-reversed.svg`](voicestead-mark-reversed.svg) | Mark only — dark backgrounds. |
| [`voicestead-mark-mono.svg`](voicestead-mark-mono.svg) | One color (`currentColor`) — tight or single-ink spots. |
| [`voicestead-lockup.svg`](voicestead-lockup.svg) | Mark + wordmark — light. Use in headers/footers. |
| [`voicestead-lockup-reversed.svg`](voicestead-lockup-reversed.svg) | Mark + wordmark — dark. |
| [`favicon.svg`](favicon.svg) | Simplified mark on an ink tile, for small sizes / the favicon set. |
| [`og-image.svg`](og-image.svg) | 1200×630 social card. **Export to PNG** for `og:image` / the GitHub repo social preview. |
| [`brand-tokens.css`](brand-tokens.css) | Ready-to-import CSS custom properties (color, type, focus ring). |
| [`voicestead-brand.md`](voicestead-brand.md) | The full guide — logo rules, color table, type, voice & tone. **Start here.** |
| [`claude-design-prompt.md`](claude-design-prompt.md) | The brief for the external marketing site (kept here so the rules live in one place). |

## Quick reference

- **Colors:** Ink Pen `#1C4066` (primary/the pen) · Voice Azure `#2A92D4` (accent/the wave) · Deep Ink `#14324F` · Azure Bright `#46A6E6` (on dark) · Steel `#7C93A8` (muted) · Mist `#EAF1F7` · Cloud `#F4F8FB` · Ink Night `#0F2437` · Ice `#DCE6EF`.
- **Type:** Fraunces (display + wordmark) · Inter (body/UI) · IBM Plex Mono (eyebrows, labels, code).
- **Minimum size:** mark ≥ 24px; below that use `favicon.svg`.

Full rules and the do-not list are in [`voicestead-brand.md`](voicestead-brand.md).

## Exporting the OG image

The social card ships as SVG. Crawlers (and GitHub's social preview) want a raster. Export a PNG once with any SVG renderer, e.g.:

```bash
# pick whichever you have installed
rsvg-convert -w 1200 -h 630 og-image.svg -o og-image.png
# or
npx --yes svgexport og-image.svg og-image.png 1200:630
```
