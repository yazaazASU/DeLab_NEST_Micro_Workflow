# NEST 2.2 UI Design Guide

> Extracted and reconstructed from the official NEST 2.2 presentation bundle (`nest_dashboard.html`).

## 1. Brand Color Tokens
- `--nest-rose`: `#DDA199` (4 px top brand hairline & secondary accent)
- `--nest-coral`: `#FF614C` (raised primary buttons & active badges; hover `#FF735F`)
- `--nest-paper`: `#F5F5F5` (warm off-white canvas)
- `--nest-surface`: `#FFFAF7` (card/header surface)
- `--nest-soft`: `#FBEFED` (soft rose highlight background)
- `--nest-ink`: `#302B2A` (primary text & focus ring)
- `--nest-muted`: `#625753` (secondary labels)
- `--nest-line`: `#D5C9C5` (hairline borders)
- `--nest-edge`: `#A3473A` (deep terracotta border/accent)
- Status tokens: `--nest-success: #246247` (`#EAF5EF`), `--nest-warning: #775014` (`#FFF5E5`), `--nest-error: #A12B3A` (`#FCEEF0`)

## 2. Typography
- Primary UI & Display Font: `"Funnel Display", "Aptos", "Segoe UI", Arial, sans-serif` (weights 300–800; local TTF at `UI Handover/fonts/FunnelDisplay.ttf` with system sans fallback).
- Base size: `15px` / `1.55` line height.

## 3. Header & Two-Tab Architecture
- **Header (`nest-header`):** 4 px `--nest-rose` top border, inline NEST wordmark SVG + `1px` divider + DeLab mark SVG, plot title/subtitle, global `Summary View | Detailed Briefs` toggle, and Tab switcher:
  1. **Tab 1 (Default) — `Project Proposals (5 Cards)`:** `#1`–`#5` Project Jump Bar + 5 full-width proposal cards.
  2. **Tab 2 — `3-Engine Analysis Maps`:** Synchronized 3-column Leaflet maps (**Crystals**, **Cells**, **Corals**) with 6 Nature-First Spatial Force toggles, `Multi-Force Synergy (2+ / 3+)`, `Hidden Potential`, Top-5 boundary overlays, and an interactive **Cell-Click Inspection Drawer**.
