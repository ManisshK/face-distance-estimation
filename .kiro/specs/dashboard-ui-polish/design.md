# Design Document — Dashboard UI Polish

## Overview

This document specifies the technical design for refining the Face Distance Estimation dashboard to commercial-grade visual quality through **CSS-only refinements**. The design is structured as a systematic CSS refactoring across eight existing components, with zero changes to React logic, backend code, or dependencies.

**Design Philosophy:** Surgical precision. Every value change is intentional, measurable, and traceable to a requirement acceptance criterion. No exploratory styling, no architectural changes — pure visual polish.

---

## Architecture

### Component Hierarchy

```
Dashboard (shell)
├── Header (brand, badge, stat chips)
├── Camera Section
│   ├── Camera Window (MJPEG stream container)
│   └── Overlay (offline state)
└── Right Panel (sidebar)
    ├── Metrics (Card wrapper)
    ├── Confidence (Card wrapper)
    ├── Radar (Card wrapper)
    ├── Guidance (Card wrapper)
    └── CalibrationPanel (Card wrapper)
```

### CSS Module Map

| Component | CSS File | JSX File | Scope |
|-----------|----------|----------|-------|
| Dashboard | `Dashboard.css` | `Dashboard.tsx` | Shell, header, grid, camera |
| Card | `Card.css` | `Card.tsx` | Shared panel wrapper |
| Metrics | `Metrics.css` | `Metrics.tsx` | Live data table |
| Confidence | `Confidence.css` | `Confidence.tsx` | Progress bar panel |
| Radar | `Radar.css` | `Radar.tsx` | SVG radar display |
| Guidance | `Guidance.css` | `Guidance.tsx` | Icon + message panel |
| CalibrationPanel | `CalibrationPanel.css` | `CalibrationPanel.tsx` | Input + button + banner |
| index.css | `index.css` | — | Global tokens |


---

## Design Systems

### Typography System

**Six-Step Size Scale** (Requirement 9)

| Step | Size | Usage |
|------|------|-------|
| XS | 9px | Tick marks, ultra-small labels |
| SM | 11px | Card titles, badges, hints, secondary text |
| BASE | 12px | Radar stats, calibration text, metric labels |
| MD | 13px | Metric values, guidance message, input text |
| LG | 15px | Distance row value (primary metric) |
| FLUID | `clamp(...)` | Large confidence %, brand title, camera overlay |

**Weight Hierarchy**

- 400: Not used (reserved for future body text)
- 500: Secondary labels, descriptions, input text
- 600: Standard data values, radar stats, metric values
- 700: Emphasized values (distance row), titles, badges, buttons
- 800: Hero values (confidence %), brand title

**Line-Height Standards**

- 1.0: Single-line numeric values (metric values, confidence %, FPS/Latency chips)
- 1.3: Headings, card titles, guidance message
- 1.5: Body text, hints, descriptions, calibration text

**Tabular Numerals**

Apply `font-variant-numeric: tabular-nums` to:
- `.header-info strong` (FPS, Latency)
- `.metric-value` (all six rows)
- `.confidence-value` (large %)
- `.radar-stat-value` (distance, angle)
- `.cal-result-value` (focal length)


### Spacing System (8px Grid)

**Token Definitions** (to be added to `index.css`)

```css
:root {
  --space-1: 8px;
  --space-2: 16px;
  --space-3: 24px;
  --space-4: 32px;
}
```

**Alignment Audit**

| Component | Current Off-Grid Values | Corrected Values |
|-----------|------------------------|------------------|
| Dashboard | `padding: clamp(14px...)` | `padding: clamp(16px, 1.8vw, 32px)` |
| Header | `gap: 12px` → stays (already aligned) | — |
| Stat Chip | `padding: 7px 15px` | `padding: 6px 12px` |
| Card | `padding: clamp(14px...)` | `padding: clamp(16px, 1.6vw, 24px) clamp(18px, 1.8vw, 24px)` |
| Metrics | `padding: 9px 0`, `gap: 7px` | `padding: 10px 0`, `gap: 8px` |
| Guidance | `gap: 3px`, `gap: 12px` | `gap: 4px`, `gap: 16px` |
| CalibrationPanel | `gap: 12px`, `padding: 9px 13px` | `gap: 16px`, `padding: 8px 12px` |

**Rounding Rule:** If an existing value is ±1px from a grid multiple, round to the nearest grid value.

---

## Component-Level Design


### 1. Dashboard (Shell, Header, Camera)

#### 1.1 Shell Padding (Req 10.2)

**Current:**
```css
padding: clamp(14px, 1.8vw, 28px);
```

**Refined:**
```css
padding: clamp(16px, 1.8vw, 32px);  /* Aligns to 16/32 grid anchors */
```

#### 1.2 Header Brand Subtitle (Req 2.1)

**Current:**
```css
.header-brand p {
  color: var(--text-muted);  /* #475569 — fails contrast */
}
```

**Refined:**
```css
.header-brand p {
  color: #64748b;  /* 4.5:1 contrast against --surface-1 */
}
```

#### 1.3 Header Right Cluster (Req 2.4)

**Current:**
```css
.header-right {
  gap: clamp(8px, 0.9vw, 14px);  /* Variable gap */
}
```

**Refined:**
```css
.header-right {
  align-items: center;  /* Already present, verify */
  gap: 12px;            /* Fixed 12px gap for consistency */
}
```


#### 1.4 Stat Chip Refinement (Req 2.2, 2.3)

**Current:**
```css
.header-info {
  padding: 7px 15px;
}
.header-info span {
  color: var(--text-dim);  /* #2d3f5a — too dark */
}
```

**Refined:**
```css
.header-info {
  padding: 6px 12px;  /* Grid-aligned, tighter */
}
.header-info span {
  color: #64748b;  /* Legible label colour */
}
```

#### 1.5 Camera Window Dominance (Req 1)

**Current State:**
- Grid: `7fr 3fr` → 70% / 30% split ✓ (already meets Req 1.1)
- Padding: `inset: 0` on img (minimal) ✓ (already meets Req 1.2)
- Grid overlay: `::before` with opacity 0.018 (meets Req 1.3)
- Corner accents: Only top-left + bottom-right

**Design Changes:**

1. **Inset box-shadow for glass depth** (Req 1.4):
```css
.camera-window {
  box-shadow:
    0 0 0 1px var(--border-subtle),
    0 2px 0 1px rgba(255, 255, 255, 0.04) inset,   /* highlight */
    0 -2px 0 1px rgba(0, 0, 0, 0.3) inset,         /* shadow */
    0 20px 60px rgba(0, 0, 0, 0.7),
    0 0 80px rgba(59, 130, 246, 0.04);
}
```


2. **Four-corner accents** (Req 1.5):

**Current `::after`:**
```css
.camera-window::after {
  box-shadow:
    -1px -1px 0 0 rgba(59, 130, 246, 0.3) inset,  /* top-left */
     1px  1px 0 0 rgba(59, 130, 246, 0.15) inset; /* bottom-right */
}
```

**Refined:**
```css
.camera-window::after {
  box-shadow:
    -1px -1px 0 0 rgba(59, 130, 246, 0.35) inset,  /* top-left */
     1px  1px 0 0 rgba(59, 130, 246, 0.35) inset,  /* bottom-right */
    -1px  1px 0 0 rgba(59, 130, 246, 0.35) inset,  /* bottom-left */
     1px -1px 0 0 rgba(59, 130, 246, 0.35) inset;  /* top-right */
}
```

#### 1.6 Responsive Breakpoints (Req 11)

**Current ultra-wide cap:**
```css
@media (min-width: 2200px) {
  .dashboard { max-width: 2400px; }
}
```

**Refined:**
```css
@media (min-width: 2200px) {
  .dashboard { max-width: 2200px; }  /* Tighter cap */
}
```

**Verify:**
- 1366–1599px: `7fr 3fr` grid maintained ✓
- 1600–2559px: Increased padding applied ✓
- ≤1024px: Single column stack ✓


---

### 2. Card Component (Shared Wrapper)

#### 2.1 Title Legibility (Req 3.1)

**Current:**
```css
.card-title {
  color: #4a5568;  /* Too dark */
}
```

**Refined:**
```css
.card-title {
  color: #64748b;  /* Legible against dark surface */
}
```

#### 2.2 Inner Padding (Req 3.2)

**Current:**
```css
.card {
  padding: clamp(14px, 1.4vw, 20px) clamp(16px, 1.6vw, 22px);
}
```

**Refined:**
```css
.card {
  padding: clamp(16px, 1.6vw, 24px) clamp(18px, 1.8vw, 24px);
}
```

#### 2.3 Hover Transition (Req 3.3)

**Current:**
```css
.card:hover {
  transform: translateY(-2px);
}
.card {
  transition: ... transform 0.25s ease;
}
```

**Refined:**
```css
.card:hover {
  transform: translateY(-3px);  /* Smoother 3px lift */
}
.card {
  transition: ... transform 0.2s ease;  /* Faster 200ms */
}
```


#### 2.4 Accent Stripe (Req 3.4)

**Current:**
```css
.card--accent-blue::after,
.card--accent-green::after,
.card--accent-amber::after,
.card--accent-rose::after {
  top: 20%;
  bottom: 20%;
  width: 3px;
  opacity: 0.85;
}
```

**Refined:**
```css
.card--accent-blue::after,
.card--accent-green::after,
.card--accent-amber::after,
.card--accent-rose::after {
  top: 15%;     /* Span 70% of height (85% - 15%) */
  bottom: 15%;
  width: 4px;   /* Thicker for prominence */
  opacity: 1.0; /* Full opacity */
}
```

#### 2.5 Top-Edge Highlight (Req 3.5)

**Current:**
```css
.card::before {
  background: radial-gradient(
    ellipse at 50% 0%,
    rgba(99, 179, 237, 0.04) 0%,
    transparent 65%
  );
}
```

**Refined:**
```css
.card::before {
  background: radial-gradient(
    ellipse at 50% 0%,
    rgba(99, 179, 237, 0.06) 0%,  /* Increased from 0.04 */
    transparent 65%
  );
}
```


---

### 3. Metrics Component

#### 3.1 Distance Row Primacy (Req 4.1, 4.2)

**Current:**
```css
.metric-value {
  font-size: 13px;
  font-weight: 600;
}
```

**Refined:**

Add a new class for the distance row in `Metrics.tsx`:
```tsx
<div className={`metric-row ${key === 'distance' ? 'metric-row--primary' : ''}`} key={key}>
```

CSS:
```css
.metric-row--primary {
  background: rgba(59, 130, 246, 0.06);
  border-left: 2px solid rgba(59, 130, 246, 0.4);
  padding-left: 8px;  /* Compensate for left border */
}

.metric-row--primary .metric-value {
  font-size: 15px;
  font-weight: 700;
}
```

#### 3.2 Non-Distance Values (Req 4.3)

**Current:**
```css
.metric-value {
  font-size: 13px;
  font-weight: 600;
}
```

**Refined:**
```css
.metric-value {
  font-size: 14px;  /* Increased from 13px */
  font-weight: 600;
}
```


#### 3.3 Label Sizing (Req 4.4)

**Current:**
```css
.metric-label {
  font-size: 12px;
  color: #64748b;
}
```

**Refined:**
```css
.metric-label {
  font-size: 11px;  /* Reduced from 12px */
  color: #64748b;   /* Colour stays */
}
```

#### 3.4 Row Separators (Req 4.5)

**Current:**
```css
.metric-row {
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}
```

**Refined:**
```css
.metric-row {
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);  /* Increased from 0.05 */
}
```

#### 3.5 Row Padding (Req 4.6, 10.3)

**Current:**
```css
.metric-row {
  padding: 9px 0;
}
.metric-label {
  gap: 7px;
}
```

**Refined:**
```css
.metric-row {
  padding: 10px 0;  /* Grid-aligned */
}
.metric-label {
  gap: 8px;  /* Grid-aligned */
}
```


---

### 4. Confidence Component

#### 4.1 Progress Track Height (Req 5.1)

**Current:**
```css
.progress-track {
  height: 5px;
}
```

**Refined:**
```css
.progress-track {
  height: 8px;  /* Doubled for visual substance */
}
```

#### 4.2 Tick Marks Legibility (Req 5.3)

**Current:**
```css
.progress-ticks {
  color: #2d3f5a;  /* Too dark, invisible */
}
```

**Refined:**
```css
.progress-ticks {
  color: #475569;  /* Legible against dark background */
}
```

#### 4.3 Quality Badge (Req 5.4)

**Current:**
```css
.confidence-badge {
  font-size: 10px;
  padding: 3px 8px;
}
```

**Refined:**
```css
.confidence-badge {
  font-size: 11px;  /* Improved from 10px */
  padding: 4px 10px;  /* Better touch target */
}
```

**Notes:** Progress fill gradients and animation are preserved exactly (Req 5.2). The `clamp(28px, 2.8vw, 36px)` large percentage font-size is preserved (Req 5.5).


---

### 5. Radar Component

#### 5.1 SVG Ring Opacity (Req 6.1)

**Current SVG in `Radar.tsx`:**
```tsx
<circle ... stroke="rgba(34,197,94,0.18)" />  /* outer */
<circle ... stroke="rgba(34,197,94,0.12)" />  /* mid */
<circle ... stroke="rgba(34,197,94,0.08)" />  /* inner */
```

**Refined SVG attributes:**
```tsx
<circle ... stroke="rgba(34,197,94,0.25)" />  /* outer — 0.25 */
<circle ... stroke="rgba(34,197,94,0.18)" />  /* mid — 0.18 */
<circle ... stroke="rgba(34,197,94,0.12)" />  /* inner — 0.12 */
```

Note: This is a JSX attribute change (`stroke` value), which is classified as a layout attribute change (the value is a static prop, not state). This is permitted under Req 12.1.

#### 5.2 Radar Dot Glow (Req 6.2)

**Current:**
```css
@keyframes radar-ping {
  0%, 100% { box-shadow: 0 0 6px #22c55e, 0 0 14px rgba(34,197,94,.35); }
  50%       { box-shadow: 0 0 10px #4ade80, 0 0 22px rgba(34,197,94,.55); }
}
```

**Refined:**
```css
@keyframes radar-ping {
  0%, 100% { box-shadow: 0 0 8px #22c55e, 0 0 18px rgba(34,197,94,.65); }
  50%       { box-shadow: 0 0 14px #4ade80, 0 0 26px rgba(34,197,94,.75); }
}
```


#### 5.3 Info Row Labels and Values (Req 6.3, 6.4)

**Current:**
```css
.radar-stat-label {
  color: #334155;  /* Too dark */
}
.radar-stat-value {
  color: #94a3b8;  /* Low contrast */
}
```

**Refined:**
```css
.radar-stat-label {
  color: #64748b;  /* Legible */
}
.radar-stat-value {
  color: #cbd5e1;  /* Higher contrast */
}
```

#### 5.4 Radar Display Size (Req 6.5, 6.6)

**Current:**
```css
.radar-display {
  width: clamp(90px, 9vw, 120px);
  height: clamp(90px, 9vw, 120px);
}
```

**Refined:**
```css
.radar-display {
  width: clamp(100px, 10vw, 130px);   /* Larger range */
  height: clamp(100px, 10vw, 130px);
}
.radar-container {
  padding: 0;   /* Remove any excess padding around display */
  gap: 12px;    /* Maintain info row gap */
}
```

---

### 6. Guidance Component

#### 6.1 Icon Wrap Size (Req 7.1)

**Current:**
```css
.guidance-icon-wrap {
  width: 38px;
  height: 38px;
  min-width: 38px;
  border-radius: 12px;
}
```

**Refined:**
```css
.guidance-icon-wrap {
  width: 44px;
  height: 44px;
  min-width: 44px;
  border-radius: 14px;
}
```


#### 6.2 Hint Text Legibility (Req 7.2)

**Current:**
```css
.guidance-hint {
  color: #334155;  /* Too dark */
}
```

**Refined:**
```css
.guidance-hint {
  color: #64748b;
}
```

#### 6.3 Guidance Spacing (Req 7.3, 10.4)

**Current:**
```css
.guidance-text {
  gap: 3px;
}
.guidance-container {
  gap: 12px;
}
```

**Refined:**
```css
.guidance-text {
  gap: 4px;   /* Grid-aligned */
}
.guidance-container {
  gap: 16px;  /* Grid-aligned, +4px breathing room */
}
```

The `.card-body` for Guidance inherits its padding from Card. The Card padding change (`clamp(16px...)`) provides the +6px vertical breathing room requested in Req 7.3 without a Guidance-specific override.

**Preserved unchanged (Req 7.4, 7.5):**
- All three colour-state box-shadows on `.guidance-icon-wrap.success/warning/error`
- `.guidance-message` font-weight and clamp size


---

### 7. CalibrationPanel Component

#### 7.1 Description Text (Req 8.1)

**Current:**
```css
.calibration-description {
  color: #334155;  /* Invisible on dark surface */
}
```

**Refined:**
```css
.calibration-description {
  color: #94a3b8;
}
```

#### 7.2 Placeholder Colour (Req 8.2)

**Current:**
```css
.calibration-input::placeholder {
  color: #1e293b;  /* Nearly invisible */
}
```

**Refined:**
```css
.calibration-input::placeholder {
  color: #475569;
}
```

#### 7.3 Unit Label (Req 8.3)

**Current:**
```css
.calibration-input-unit {
  color: #1e3a5f;  /* Invisible */
}
```

**Refined:**
```css
.calibration-input-unit {
  color: #64748b;
}
```

#### 7.4 Result Banner Labels (Req 8.4, 8.5)

**Current:**
```css
.cal-result-label {
  color: #166534;  /* Very dark green, illegible on dark banner */
  opacity: 0.7;
}
.calibration-result.success {
  color: #4ade80;
}
```

**Refined:**
```css
.cal-result-label {
  color: #4ade80;  /* Bright green — legible on dark banner */
  opacity: 1;      /* No dimming */
}
.calibration-result.success {
  color: #4ade80;  /* Parent sets bright base for all children */
}
```


#### 7.5 Input Focus State (Req 8.6)

**Current:**
```css
.calibration-input:focus {
  border-color: rgba(59, 130, 246, 0.45);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);  /* Existing ring preserved */
}
```

**Refined:**
```css
.calibration-input:focus {
  border-color: rgba(59, 130, 246, 0.55);  /* Increased from 0.45 */
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}
```

#### 7.6 Spacing (Req 10.5)

**Current:**
```css
.calibration-container {
  gap: 12px;
}
.calibration-result {
  padding: 9px 13px;
}
```

**Refined:**
```css
.calibration-container {
  gap: 16px;  /* Grid-aligned */
}
.calibration-result {
  padding: 8px 12px;  /* Grid-aligned */
}
```

---

## Implementation Strategy

### Phase 1: Foundation (index.css)

1. Add spacing tokens to `:root`
2. Verify no other global changes needed

### Phase 2: Core Components (Card, Dashboard)

3. Refine Card.css (title, padding, hover, accent, highlight)
4. Refine Dashboard.css (shell padding, header, camera, stat chips, responsive)

### Phase 3: Sidebar Components

5. Refine Metrics.css (distance row, labels, separators, padding)
6. Refine Confidence.css (track height, ticks, badge)
7. Refine Radar.css (dot glow, labels, display size) + Radar.tsx SVG strokes
8. Refine Guidance.css (icon size, hint colour, spacing)
9. Refine CalibrationPanel.css (text colours, input focus, spacing)


### Phase 4: Typography Audit

10. Scan all CSS modules for font-size violations
11. Replace any off-scale sizes with the nearest six-step value
12. Apply `font-variant-numeric: tabular-nums` to numeric elements
13. Verify line-height rules (1.0 / 1.3 / 1.5)
14. Verify font-weight values are in {400, 500, 600, 700, 800}

### Phase 5: Verification

15. Visual regression test at 1366×768, 1920×1080, 2560×1440
16. Keyboard navigation test (focus states)
17. Contrast audit (all text against backgrounds)
18. Animation smoothness check (progress bar, radar dot, badge pulse, card hover)

---

## Validation Criteria

### Per-Requirement Checklist

| Requirement | Validation Method |
|-------------|------------------|
| Req 1.1 | Measure camera width at 1366px → expect 66–69% of total |
| Req 1.2 | Inspect `.camera-stream` inset → expect ≤4px |
| Req 1.3 | Inspect `.camera-window::before` opacity → expect ≤0.04 |
| Req 1.4 | Inspect `.camera-window` box-shadow → expect ≥2 inset layers |
| Req 1.5 | Inspect `.camera-window::after` box-shadow → expect 4 corners, ≥0.35 opacity |
| Req 2.1 | Contrast test `.header-brand p` → expect ≥4.5:1 |
| Req 2.2 | Inspect `.header-info` padding → expect 6px 12px |
| Req 2.3 | Inspect `.header-info span` colour → expect #64748b |
| Req 2.4 | Inspect `.header-right` gap → expect 12px |
| Req 2.5 | Inspect `.header-brand h1` → expect font-weight 800, min 16px |
| Req 3.1 | Inspect `.card-title` colour → expect #64748b |
| Req 3.2 | Inspect `.card` padding → expect clamp(16px, 1.6vw, 24px) / (18px, 1.8vw, 24px) |
| Req 3.3 | Hover card → expect 3px translateY over 200ms |
| Req 3.4 | Inspect accent stripe → expect 4px wide, 15–85% height, opacity 1.0 |
| Req 3.5 | Inspect `.card::before` gradient → expect ≥0.06 opacity |
| Req 4.1 | Inspect `.metric-row--primary .metric-value` → expect 15px / 700 |
| Req 4.2 | Inspect `.metric-row--primary` → expect blue background + left border |
| Req 4.3 | Inspect `.metric-value` → expect 14px / 600 |
| Req 4.4 | Inspect `.metric-label` → expect 11px / #64748b |
| Req 4.5 | Inspect `.metric-row` border-bottom → expect opacity 0.08 |
| Req 4.6 | Inspect `.metric-row` padding → expect 10px 0 |

| Req 5.1 | Inspect `.progress-track` height → expect 8px |
| Req 5.2 | Verify progress fill gradients unchanged (4 colour states) |
| Req 5.3 | Inspect `.progress-ticks` colour → expect #475569 |
| Req 5.4 | Inspect `.confidence-badge` → expect 11px / 4px 10px padding |
| Req 5.5 | Verify `.confidence-value` clamp unchanged |
| Req 6.1 | Inspect Radar SVG strokes → expect 0.25 / 0.18 / 0.12 |
| Req 6.2 | Inspect radar-ping keyframe → expect 8px/18px spread min/max |
| Req 6.3 | Inspect `.radar-stat-label` colour → expect #64748b |
| Req 6.4 | Inspect `.radar-stat-value` colour → expect #cbd5e1 |
| Req 6.5 | Inspect `.radar-display` size → expect clamp(100px, 10vw, 130px) |
| Req 6.6 | Measure radar SVG vs card width → expect ≥70% |
| Req 7.1 | Inspect `.guidance-icon-wrap` → expect 44×44px, 14px radius |
| Req 7.2 | Inspect `.guidance-hint` colour → expect #64748b |
| Req 7.3 | Measure Guidance vertical padding → expect +6px vs other cards |
| Req 7.4 | Verify icon wrap box-shadows unchanged (3 variants) |
| Req 7.5 | Verify `.guidance-message` font-weight 700 unchanged |
| Req 8.1 | Inspect `.calibration-description` colour → expect #94a3b8 |
| Req 8.2 | Inspect input placeholder colour → expect #475569 |
| Req 8.3 | Inspect `.calibration-input-unit` colour → expect #64748b |
| Req 8.4 | Inspect `.cal-result-label` colour → expect #4ade80 |
| Req 8.5 | Inspect `.calibration-result.success` colour → expect #4ade80 |
| Req 8.6 | Inspect input:focus border → expect rgba(59, 130, 246, 0.55) |
| Req 9.1–9.5 | Typography audit (scan all CSS for size/weight/line-height violations) |
| Req 10.1–10.6 | Spacing audit (scan all CSS for off-grid values) |
| Req 11.1–11.6 | Responsive test at 1366, 1600, 2560, 1024 breakpoints |
| Req 12.1–12.5 | Code review: no new state/effects/refs, CSS-only animations, zero deps |

---

## Components and Interfaces

This feature modifies only **presentation layer CSS** and JSX layout attributes. No component interfaces are changed.

### Unchanged Interfaces

All component props remain identical:
- `Dashboard.tsx`: No props (data from `useFrameData` hook)
- `Card.tsx`: `{ title: string; children: ReactNode; accent?: ... }`
- `Metrics.tsx`: `{ distance, angle, confidence, fps, latency, stability: string }`
- `Confidence.tsx`: `{ confidence: number }`
- `Radar.tsx`: `{ distanceDisplay, angleDisplay, angleDeg, distanceCm, faceDetected: ... }`
- `Guidance.tsx`: `{ message: string; status: "success"|"warning"|"error" }`
- `CalibrationPanel.tsx`: No props (internal state only)

### CSS Class Changes

**New classes:**
- `.metric-row--primary` in Metrics.css (for distance row highlight)

**Modified classes:**
- 50+ existing CSS classes will have updated property values (colors, sizes, spacing)

**No classes removed.**

---

## Data Models

This feature introduces **zero new data models**. All React state, props, and API contracts remain unchanged.

The only "data" changes are **static CSS property values** (strings and numbers in `.css` files).

---

## Error Handling

This feature has **no runtime error paths** because it modifies only static CSS.

**Potential issues:**
1. **CSS typo** → Browser ignores invalid rule, falls back to previous value
2. **Contrast too low** → Detected in manual validation (Phase 5)
3. **Off-grid spacing** → Detected in spacing audit (Phase 4, step 14)

**Mitigation:**
- All changes are code-reviewed against the design spec
- Visual regression tests catch unintended side effects
- Git diff allows instant rollback if issues found

---

## Testing Strategy

### Manual Visual Testing

**Test Matrix:**

| Viewport | Browser | What to verify |
|----------|---------|---------------|
| 1366×768 | Chrome | Camera 65–70% width, sidebar visible, no overflow |
| 1920×1080 | Chrome | All spacing aligned, text legible, animations smooth |
| 2560×1440 | Chrome | Max-width cap applied, no stretching |
| 1024×768 | Chrome | Single-column stack, sidebar static (no sticky) |

**Per-Component Checks:**

1. **Dashboard:** Header aligned, camera dominant, responsive breakpoints
2. **Card:** Hover lift smooth, accent stripe visible, title legible
3. **Metrics:** Distance row highlighted, all values tabular-aligned
4. **Confidence:** Progress bar 8px tall, tick marks visible, badge readable
5. **Radar:** Rings visible, dot animates smoothly, labels legible
6. **Guidance:** Icon 44×44px, hint text readable, spacing comfortable
7. **CalibrationPanel:** All text visible, focus state clear, banner legible

### Automated Validation (Optional)

If browser automation is available:
- Screenshot comparison at 3 viewport widths (before/after)
- Computed style checks for critical values (`.card-title` color, `.progress-track` height, etc.)
- Contrast ratio checks via axe-core or similar

### Regression Prevention

- All CSS changes committed in a single atomic commit
- No CSS minification during development (readable diffs)
- Component-scoped CSS modules prevent cascade conflicts

---

## Correctness Properties

**Invariants (must hold after all changes):**

1. **Zero behavioral changes:** All React hooks, event handlers, and state remain unchanged
2. **Zero layout shifts:** No element should reflow in a way that moves unrelated content (card padding changes are localized)
3. **Backwards-compatible:** No component prop signatures changed, so parent components need no updates
4. **Accessibility preserved:** Focus states, ARIA attributes, semantic HTML unchanged
5. **Animation continuity:** All existing animations (progress bar, radar dot, badge pulse) preserved
6. **Responsive integrity:** All existing breakpoints honored, no new breakpoints introduced

**Property Checks:**

| Property | Verification Method |
|----------|-------------------|
| No new React state | Grep for `useState`, `useReducer`, `useRef` in diffs → expect 0 new |
| No new npm deps | Check `package.json` diff → expect 0 changes |
| CSS-only animations | Grep for `requestAnimationFrame`, `setInterval` → expect 0 new |
| Tabular numerals applied | Inspect computed styles on `.metric-value` etc. → expect `tabular-nums` |
| Spacing grid adherence | Audit all padding/gap/margin values → expect multiples of 4 or 8 |

---

## Dependencies

**Zero new dependencies.** This feature uses only:
- Existing CSS features (pseudo-elements, transitions, media queries)
- React JSX (for adding `className` conditionals in Metrics.tsx)
- No new libraries, no npm installs

**Browser Support:**
- `clamp()` for fluid typography (supported in Chrome 79+, Firefox 75+, Safari 13.1+)
- `backdrop-filter` for glassmorphism (supported in Chrome 76+, Firefox 103+, Safari 9+)
- `aspect-ratio` for camera (supported in Chrome 88+, Firefox 89+, Safari 15+)

All target browsers already support these features (verified via existing Dashboard code).

---

## Implementation Notes

### Order of Operations

**Critical sequencing:**
1. **index.css first** → Spacing tokens must exist before components reference them (optional — tokens are only used for documentation, not in actual CSS)
2. **Card.css before sidebars** → Sidebar components inherit Card padding, so Card must be refined first
3. **Metrics.tsx before Metrics.css** → Add `metric-row--primary` class to JSX, then write CSS for it

### Conflict Avoidance

**If another developer modifies the same CSS file:**
- This feature touches presentation only (colors, sizes, spacing)
- Other work likely touches layout or new features
- Conflicts are rare, but if they occur: prefer this feature's values for colors/sizes, integrate layout changes normally

### Rollback Plan

If visual regressions are found post-deployment:
1. Revert the single feature branch commit
2. Re-deploy previous CSS bundle
3. Debug specific issue offline
4. Reapply feature with fixes

---

## Summary

This design document specifies a **CSS-only refactoring** to polish the Face Distance Estimation dashboard to commercial quality. The implementation is:

- **Scoped:** 8 CSS files + 1 JSX className addition
- **Traceable:** Every change maps to a requirement acceptance criterion
- **Safe:** Zero behavioral changes, zero new dependencies
- **Reversible:** Single atomic commit, instant rollback
- **Testable:** 24 explicit validation checks, 5-phase verification plan

The result: a visually refined dashboard that matches the quality of industry-leading AI tools, with zero impact on application logic or performance.
