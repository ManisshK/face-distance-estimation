# Requirements Document

## Introduction

This feature polishes the visual presentation of the Face Distance Estimation frontend to commercial-grade quality — on par with dashboards from OpenAI, Linear, Vercel, NVIDIA Omniverse, Tesla Vision, and Apple Vision Pro. The application is fully feature-complete; this work targets only CSS and JSX layout within the existing eight components. No backend code, API calls, hooks, services, camera logic, detection logic, or calibration logic may be touched. The result must look intentional, legible, and refined at every breakpoint from 1366 × 768 up to 2560 × 1440.

## Glossary

- **Dashboard**: The top-level component (`Dashboard.tsx / Dashboard.css`) that renders the app shell, header, and main grid.
- **Card**: The reusable panel wrapper (`Card.tsx / Card.css`) with a glassmorphism background, title row, and optional left-edge accent stripe.
- **Metrics**: The `Metrics.tsx / Metrics.css` component that renders a six-row live data table (Distance, Angle, Confidence, FPS, Latency, Stability).
- **Confidence**: The `Confidence.tsx / Confidence.css` component that renders the large percentage value, animated progress bar, and quality badge.
- **Radar**: The `Radar.tsx / Radar.css` component that renders an SVG radar display with an animated dot and an info row.
- **Guidance**: The `Guidance.tsx / Guidance.css` component that renders a status icon, guidance message, and hint text.
- **CalibrationPanel**: The `CalibrationPanel.tsx / CalibrationPanel.css` component that renders a distance input, calibrate button, and result banner.
- **Header**: The `dashboard-header` element inside Dashboard that contains the brand block and the right stat cluster.
- **Camera_Window**: The `camera-window` container inside Dashboard that hosts the MJPEG stream and the offline overlay.
- **Spacing_System**: The 8 px grid token system defined in `index.css` and consumed across all component CSS files.
- **Typography_System**: The consistent size scale, weight, and line-height rules applied across all component CSS files.
- **Accent_Stripe**: The `::after` pseudo-element on `.card` that renders the left-edge colour stripe.
- **Stat_Chip**: The `.header-info` element in the Header that displays FPS or Latency.
- **Distance_Row**: The first row of the Metrics table, labelled "Distance", designated as the primary metric.
- **Progress_Track**: The `.progress-track` element in Confidence that acts as the progress bar background.
- **Progress_Fill**: The `.progress-fill` element in Confidence that animates to the current confidence percentage.
- **Tick_Marks**: The `.progress-ticks` element in Confidence that labels 0, 50, and 100 on the progress bar.
- **Radar_Dot**: The `.radar-dot` element in Radar that moves horizontally to represent face angle.
- **Info_Row**: The `.radar-info` element in Radar that shows Distance and Angle stats below the SVG.
- **CSS_Module**: A per-component `.css` file whose class names are scoped to that component.

---

## Requirements

### Requirement 1: Camera Section Visual Dominance

**User Story:** As a user, I want the camera feed to feel like the dominant hero element of the dashboard, so that the live video commands immediate visual attention.

#### Acceptance Criteria

1. THE Camera_Window SHALL occupy a grid column width ratio of no less than 65 % and no more than 70 % of the total dashboard grid width at viewport widths of 1366 px and above.
2. THE Camera_Window SHALL apply a maximum padding of 4 px between its own border edge and the `<img>` stream element, so the video almost fills the card.
3. WHEN the camera stream is active, THE Camera_Window SHALL display a semi-transparent scan-line or subtle grid overlay with line opacity no greater than 0.04, rendered via a CSS `::before` pseudo-element without touching JavaScript.
4. THE Camera_Window SHALL apply an inner box-shadow of at least two layers — one inset highlight and one inset shadow — to create a glass-depth effect visible at all times.
5. THE Camera_Window SHALL render corner-accent lines on all four corners (not only top-left and bottom-right) using the existing `::after` pseudo-element technique, with a blue accent opacity of at least 0.35.

---

### Requirement 2: Header Spacing, Typography, and Stat Chips

**User Story:** As a user, I want the dashboard header to feel polished and immediately readable, so that the brand, status, and live stats are all legible at a glance.

#### Acceptance Criteria

1. THE Header SHALL vertically align the brand subtitle text (`.header-brand p`) to a colour with a minimum contrast ratio of 4.5 : 1 against `--surface-1`, replacing the current `--text-muted` (`#475569`) token.
2. THE Stat_Chip SHALL use a padding of exactly 6 px top/bottom and 12 px left/right, reducing the current 7 px / 15 px values to tighten visual bulk.
3. THE Stat_Chip label text (`.header-info span`) SHALL use a colour of at least `#64748b` (replacing `--text-dim` `#2d3f5a`) so it reads legibly against the chip background.
4. THE Header SHALL vertically align all right-cluster children (badge, stat chips) to `center` with a consistent gap of 12 px, verified across both 1366 px and 1920 px widths.
5. THE Header brand title (`.header-brand h1`) SHALL maintain `font-weight: 800` and a minimum font size of 16 px at all viewport widths.

---

### Requirement 3: Card System Consistency

**User Story:** As a developer and user, I want every Card to have consistent, legible titles and a refined hover behaviour, so that the panel hierarchy is immediately clear.

#### Acceptance Criteria

1. THE Card title (`.card-title`) SHALL use a colour of at least `#64748b`, replacing the current `#4a5568` value, to ensure legibility against the card background.
2. THE Card SHALL apply consistent inner padding using the Spacing_System: `clamp(16px, 1.6vw, 24px)` top/bottom and `clamp(18px, 1.8vw, 24px)` left/right, replacing existing `clamp(14px…)` values.
3. WHEN a Card is hovered, THE Card SHALL transition `translateY` by a maximum of 3 px over 200 ms, replacing the current abrupt 2 px / 250 ms transition.
4. THE Accent_Stripe SHALL be 4 px wide (replacing the current 3 px), span from 15 % to 85 % of the card height, and have opacity 1.0 (replacing 0.85) for improved visibility.
5. THE Card SHALL display a radial-gradient top-edge highlight (`::before`) that is visible at a minimum opacity of 0.06 (replacing the current 0.04).

---

### Requirement 4: Metrics Panel Hierarchy

**User Story:** As a user, I want the Metrics panel to present live data with clear visual hierarchy, so that the most important value — distance — stands out and every value is readable at a glance.

#### Acceptance Criteria

1. THE Distance_Row SHALL render the metric value at `font-size: 15px` and `font-weight: 700`, visually distinguishing it from all other rows.
2. THE Distance_Row SHALL apply a background highlight of `rgba(59, 130, 246, 0.06)` and a left-border accent of `2px solid rgba(59, 130, 246, 0.4)` to communicate primacy.
3. THE Metrics component SHALL render all non-distance metric values at a minimum `font-size` of 14 px and `font-weight: 600` (replacing the current 13 px / 600).
4. THE Metrics component SHALL render all metric labels at `font-size: 11px` and `color: #64748b` (replacing 12 px / `#64748b` — keeping the colour but reducing competing size).
5. THE Metrics component SHALL render row separators with `border-bottom: 1px solid rgba(255, 255, 255, 0.08)` (replacing the current 0.05 opacity) for legible separation.
6. THE Metrics component SHALL apply row padding of exactly `10px 0` (replacing the current `9px 0`) to align with the Spacing_System 8 px grid.

---

### Requirement 5: Confidence Panel

**User Story:** As a user, I want the Confidence panel to communicate signal strength clearly through a bold progress bar and readable tick marks, so that I can assess detection quality instantly.

#### Acceptance Criteria

1. THE Progress_Track SHALL have a height of 8 px (replacing the current 5 px) to be visually substantial.
2. THE Progress_Fill SHALL maintain its four colour-state gradients (excellent / good / fair / poor) and animate `width` over 500 ms without modification.
3. THE Tick_Marks SHALL use a colour of `#475569` (replacing `#2d3f5a`) so that `0`, `50`, and `100` labels are legible against the dark background.
4. THE Confidence component SHALL render the quality badge with `font-size: 11px` and `padding: 4px 10px` (replacing 10 px / 3 px 8 px) for improved touch target and legibility.
5. THE Confidence component SHALL preserve the `clamp(28px, 2.8vw, 36px)` large percentage value unchanged.

---

### Requirement 6: Radar Display

**User Story:** As a user, I want the Radar panel to feel vivid and informative, so that the face-position dot and stat labels are always clearly visible.

#### Acceptance Criteria

1. THE Radar component SHALL render its inner rings at stroke opacity values of at least 0.25, 0.18, and 0.12 (outermost to innermost), replacing 0.18 / 0.12 / 0.08.
2. THE Radar_Dot active state SHALL animate between a minimum `box-shadow` spread of `0 0 8px #22c55e` and a maximum of `0 0 18px rgba(34, 197, 94, 0.65)`, replacing the current 6 px / 14 px values.
3. THE Info_Row stat labels (`.radar-stat-label`) SHALL use `color: #64748b` (replacing `#334155`) so they read legibly.
4. THE Info_Row stat values (`.radar-stat-value`) SHALL use `color: #cbd5e1` (replacing `#94a3b8`) for higher contrast.
5. THE Radar display container SHALL use `width: clamp(100px, 10vw, 130px)` and `height: clamp(100px, 10vw, 130px)` (replacing `clamp(90px…120px)`) to make better use of the sidebar width.
6. THE Radar container padding around the display SHALL be reduced so the radar SVG occupies at least 70 % of the card content width.

---

### Requirement 7: Guidance Panel

**User Story:** As a user, I want the Guidance panel to draw attention with a clear icon and readable hint text, so that I immediately know which action to take.

#### Acceptance Criteria

1. THE Guidance component icon wrap (`.guidance-icon-wrap`) SHALL have dimensions of 44 × 44 px (replacing 38 × 38 px) and `border-radius: 14px`.
2. THE Guidance component hint text (`.guidance-hint`) SHALL use `color: #64748b` (replacing `#334155`) so the hint is legible against the card background.
3. THE Guidance component SHALL apply a top/bottom card body padding that gives the content at least 6 px additional vertical breathing room compared to other cards.
4. THE Guidance component icon wrap SHALL maintain its three colour-state variants (success / warning / error) with their respective glow box-shadows unchanged.
5. THE Guidance component message text (`.guidance-message`) SHALL preserve `font-weight: 700` and its `clamp(13px, 1.1vw, 15px)` size.

---

### Requirement 8: Calibration Panel Legibility

**User Story:** As a user, I want all text in the Calibration panel to be clearly readable, so that I can follow the instructions, interact with the input, and understand the result.

#### Acceptance Criteria

1. THE CalibrationPanel description text (`.calibration-description`) SHALL use `color: #94a3b8` (replacing `#334155`) to achieve legibility against the dark card surface.
2. THE CalibrationPanel input placeholder SHALL use `color: #475569` (replacing `#1e293b`) so placeholder text is visible before the user types.
3. THE CalibrationPanel unit label (`.calibration-input-unit`) SHALL use `color: #64748b` (replacing `#1e3a5f`) so the "cm" suffix is visible against the input background.
4. THE CalibrationPanel result label (`.cal-result-label`) SHALL use `color: #4ade80` (replacing `#166534`) so the "Focal length" label is legible on the dark success banner.
5. THE CalibrationPanel result banner (`.calibration-result.success`) SHALL have its `color` token set to `#4ade80` for all child text unless overridden by a more specific rule.
6. THE CalibrationPanel input border SHALL transition to `rgba(59, 130, 246, 0.55)` on `:focus`, preserving the existing `box-shadow` focus ring.

---

### Requirement 9: Typography System

**User Story:** As a developer, I want a consistent typography scale and weight system applied across all components, so that the UI feels cohesive and professionally designed.

#### Acceptance Criteria

1. THE Typography_System SHALL define a base size scale with six steps — 9 px, 11 px, 12 px, 13 px, 15 px, and a fluid heading using `clamp` — applied consistently across all CSS Modules.
2. THE Typography_System SHALL enforce `font-weight` values from the set {400, 500, 600, 700, 800} only, with no values outside this set present in any CSS Module.
3. THE Typography_System SHALL standardise `line-height` to 1.0 for single-line numeric values, 1.3 for headings, and 1.5 for body/hint text across all components.
4. THE Typography_System SHALL use `font-variant-numeric: tabular-nums` on every element that renders a live numeric value (distance, angle, confidence, FPS, latency).
5. THE Typography_System SHALL eliminate all font-size values that do not belong to the six-step scale defined in Criterion 1 of this requirement; any such values SHALL be replaced with the nearest step.

---

### Requirement 10: Spacing System (8 px Grid)

**User Story:** As a developer, I want all spacing values to follow a strict 8 px grid, so that the layout feels intentional and harmonious across components.

#### Acceptance Criteria

1. THE Spacing_System SHALL define spacing tokens as multiples of 8 px: `--space-1: 8px`, `--space-2: 16px`, `--space-3: 24px`, `--space-4: 32px` in `index.css`.
2. THE Dashboard SHALL replace its current `padding: clamp(14px…28px)` with `clamp(16px, 1.8vw, 32px)` to align outer padding with the 8 px grid.
3. THE Metrics component SHALL replace `padding: 9px 0` with `padding: 10px 0` and `gap: 7px` icon gap with `gap: 8px`, aligning both to the nearest grid multiple.
4. THE Guidance component SHALL replace `gap: 3px` text-block gap with `gap: 4px` and `gap: 12px` container gap with `gap: 16px`.
5. THE CalibrationPanel SHALL replace `gap: 12px` container gap with `gap: 16px` and `padding: 9px 13px` result banner with `padding: 8px 12px`.
6. IF a component uses an odd spacing value (7 px, 9 px, 3 px, etc.) not reducible to a clean 8 px multiple, THEN THE component SHALL round the value to the nearest 8 px multiple without altering the component's visual proportion by more than 1 px.

---

### Requirement 11: Responsiveness

**User Story:** As a user, I want the dashboard to render correctly and look polished on laptops at 1366 × 768, standard monitors at 1920 × 1080, and wide displays at 2560 × 1440, so that the experience is consistent across hardware.

#### Acceptance Criteria

1. WHILE the viewport width is between 1366 px and 1599 px, THE Dashboard grid SHALL maintain a `7fr 3fr` column ratio and all sidebar cards SHALL remain fully visible without horizontal overflow.
2. WHILE the viewport width is between 1600 px and 2559 px, THE Dashboard SHALL apply a slightly increased outer padding via the existing `@media (min-width: 1600px)` rule, scaled to the 8 px grid.
3. WHILE the viewport width is 2560 px or greater, THE Dashboard max-width cap SHALL be set to `2200px` (reducing from the current `2400px`) to prevent excessively wide layouts.
4. WHILE the viewport width is 1024 px or less, THE Dashboard grid SHALL collapse to a single column with the camera above the sidebar, and the sidebar SHALL become static (no sticky positioning).
5. THE right-panel sticky scroll container SHALL not clip card content at any viewport height between 600 px and 1080 px.
6. THE Camera_Window `aspect-ratio: 16 / 9` SHALL be preserved at all breakpoints so the video container never distorts.

---

### Requirement 12: Rendering Performance

**User Story:** As a developer, I want all visual changes to be implemented exclusively through CSS without introducing additional React re-renders, so that the application's runtime performance is not degraded.

#### Acceptance Criteria

1. THE Dashboard_UI_Polish feature SHALL modify only CSS Module files and JSX layout attributes (className, inline style values derived from existing props) — no new React state, effects, refs, or event listeners may be introduced.
2. THE Dashboard_UI_Polish feature SHALL use CSS `transition` and `@keyframes` for all animations (hover lifts, progress bar, radar dot, badge pulse) — no JavaScript animation libraries or `requestAnimationFrame` calls.
3. THE Dashboard_UI_Polish feature SHALL use CSS `will-change: transform` exclusively on elements that are already animated, and SHALL NOT apply it to static elements.
4. IF a visual effect (gradient, shadow, overlay) can be achieved with a CSS pseudo-element (`::before`, `::after`), THEN THE implementation SHALL prefer the pseudo-element over an additional JSX DOM node.
5. THE Dashboard_UI_Polish feature SHALL introduce zero new npm dependencies and zero new React component files.
