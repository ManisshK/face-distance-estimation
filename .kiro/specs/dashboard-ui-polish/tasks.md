# Implementation Plan: Dashboard UI Polish

## Overview
Refine the Face Distance Estimation dashboard to commercial-grade visual quality through CSS-only changes across 8 component files. No backend, hooks, services, or new dependencies are touched.

## Tasks

- [ ] 1. Add spacing tokens to index.css
  - Open `frontend/src/index.css`
  - Add `--space-1: 8px`, `--space-2: 16px`, `--space-3: 24px`, `--space-4: 32px` to `:root`
  - **Files:** `frontend/src/index.css`
  - **Requirements:** Req 10.1

- [ ] 2. Refine Card component styles
  - Update `.card-title` color to `#64748b`
  - Update `.card` padding to `clamp(16px, 1.6vw, 24px) clamp(18px, 1.8vw, 24px)`
  - Update `.card` transition transform duration to `0.2s`
  - Update `.card:hover` transform to `translateY(-3px)`
  - Update accent stripe pseudo-elements: `top: 15%`, `bottom: 15%`, `width: 4px`, `opacity: 1.0`
  - Update `.card::before` radial-gradient opacity from `0.04` to `0.06`
  - **Files:** `frontend/src/components/Common/Card.css`
  - **Requirements:** Req 3.1, 3.2, 3.3, 3.4, 3.5

- [ ] 3. Refine Dashboard shell and header styles
  - Update `.dashboard` padding to `clamp(16px, 1.8vw, 32px)`
  - Update `.header-brand p` color to `#64748b`
  - Update `.header-right` gap to `12px`
  - Update `.header-info` padding to `6px 12px`
  - Update `.header-info span` color to `#64748b`
  - **Files:** `frontend/src/components/Dashboard.css`
  - **Requirements:** Req 2.1, 2.2, 2.3, 2.4, 10.2


- [ ] 4. Refine Camera Window styling
  - Update `.camera-window` box-shadow to add inset highlight (`0 2px 0 1px rgba(255, 255, 255, 0.04) inset`) and inset shadow (`0 -2px 0 1px rgba(0, 0, 0, 0.3) inset`)
  - Update `.camera-window::after` box-shadow to include all four corners with `rgba(59, 130, 246, 0.35)` opacity
  - Update `@media (min-width: 2200px)` max-width from `2400px` to `2200px`
  - **Files:** `frontend/src/components/Dashboard.css`
  - **Requirements:** Req 1.4, 1.5, 11.3

- [ ] 5. Add distance row highlighting to Metrics component
  - Modify `Metrics.tsx` to add conditional class: `className={metric-row ${key === 'distance' ? 'metric-row--primary' : ''}}`
  - Add `.metric-row--primary` CSS with blue background, left border, and padding-left compensation
  - Add `.metric-row--primary .metric-value` with `font-size: 15px` and `font-weight: 700`
  - **Files:** `frontend/src/components/Metrics.tsx`, `frontend/src/components/Metrics.css`
  - **Requirements:** Req 4.1, 4.2

- [ ] 6. Refine Metrics component general styles
  - Update `.metric-value` font-size to `14px`
  - Update `.metric-label` font-size to `11px`
  - Update `.metric-row` border-bottom opacity to `0.08`
  - Update `.metric-row` padding to `10px 0`
  - Update `.metric-label` gap to `8px`
  - **Files:** `frontend/src/components/Metrics.css`
  - **Requirements:** Req 4.3, 4.4, 4.5, 4.6, 10.3

- [ ] 7. Refine Confidence component styles
  - Update `.progress-track` height to `8px`
  - Update `.progress-ticks` color to `#475569`
  - Update `.confidence-badge` font-size to `11px`
  - Update `.confidence-badge` padding to `4px 10px`
  - **Files:** `frontend/src/components/Confidence.css`
  - **Requirements:** Req 5.1, 5.3, 5.4


- [ ] 8. Refine Radar component SVG and CSS
  - Update SVG ring stroke opacities in `Radar.tsx`: outer `0.25`, middle `0.18`, inner `0.12`
  - Update `@keyframes radar-ping` in `Radar.css`: 0%/100% to `0 0 8px #22c55e, 0 0 18px rgba(34,197,94,.65)`, 50% to `0 0 14px #4ade80, 0 0 26px rgba(34,197,94,.75)`
  - Update `.radar-stat-label` color to `#64748b`
  - Update `.radar-stat-value` color to `#cbd5e1`
  - Update `.radar-display` size to `clamp(100px, 10vw, 130px)` for both width and height
  - **Files:** `frontend/src/components/Radar.tsx`, `frontend/src/components/Radar.css`
  - **Requirements:** Req 6.1, 6.2, 6.3, 6.4, 6.5, 6.6

- [ ] 9. Refine Guidance component styles
  - Update `.guidance-icon-wrap` dimensions to `44px` × `44px`, min-width `44px`
  - Update `.guidance-icon-wrap` border-radius to `14px`
  - Update `.guidance-hint` color to `#64748b`
  - Update `.guidance-text` gap to `4px`
  - Update `.guidance-container` gap to `16px`
  - **Files:** `frontend/src/components/Guidance.css`
  - **Requirements:** Req 7.1, 7.2, 7.3, 10.4

- [ ] 10. Refine CalibrationPanel component styles
  - Update `.calibration-description` color to `#94a3b8`
  - Update `.calibration-input::placeholder` color to `#475569`
  - Update `.calibration-input-unit` color to `#64748b`
  - Update `.cal-result-label` color to `#4ade80` and remove/set opacity to `1`
  - Update `.calibration-input:focus` border-color to `rgba(59, 130, 246, 0.55)`
  - Update `.calibration-container` gap to `16px`
  - Update `.calibration-result` padding to `8px 12px`
  - **Files:** `frontend/src/components/CalibrationPanel.css`
  - **Requirements:** Req 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 10.5


- [ ] 11. Typography system audit and corrections
  - Scan all CSS modules for font-size values outside the 6-step scale (9px, 11px, 12px, 13px, 15px, clamp)
  - Replace any off-scale font-size values with the nearest valid step
  - Verify no font-weight values outside {400, 500, 600, 700, 800}
  - Verify line-height is 1.0 on numeric values, 1.3 on headings, 1.5 on body/hint text
  - Ensure `font-variant-numeric: tabular-nums` on `.header-info strong`, `.metric-value`, `.confidence-value`, `.radar-stat-value`, `.cal-result-value`
  - **Files:** `frontend/src/components/Dashboard.css`, `frontend/src/components/Common/Card.css`, `frontend/src/components/Metrics.css`, `frontend/src/components/Confidence.css`, `frontend/src/components/Radar.css`, `frontend/src/components/Guidance.css`, `frontend/src/components/CalibrationPanel.css`
  - **Requirements:** Req 9.1, 9.2, 9.3, 9.4, 9.5

- [ ] 12. Final spacing audit and cleanup
  - Verify all padding, gap, and margin values across all CSS modules align to the 8px grid
  - Fix any remaining odd values (e.g. 7px, 9px, 3px) by rounding to the nearest grid multiple
  - Cross-check that all spacing changes from tasks 2–10 were applied correctly
  - Verify responsive breakpoints: `7fr 3fr` grid at 1366–1599px, increased padding at 1600px+, single column at ≤1024px
  - **Files:** All modified CSS files
  - **Requirements:** Req 10.6, 11.1, 11.2, 11.4, 11.5, 11.6, 12.1, 12.2, 12.3, 12.4, 12.5

## Task Dependency Graph

```json
{
  "waves": [
    { "wave": 1, "tasks": [1] },
    { "wave": 2, "tasks": [2] },
    { "wave": 3, "tasks": [3, 5, 7, 8, 9, 10] },
    { "wave": 4, "tasks": [4, 6] },
    { "wave": 5, "tasks": [11] },
    { "wave": 6, "tasks": [12] }
  ],
  "dependencies": {
    "2": [1],
    "3": [2],
    "4": [3],
    "5": [2],
    "6": [5],
    "7": [2],
    "8": [2],
    "9": [2],
    "10": [2],
    "11": [3, 4, 6, 7, 8, 9, 10],
    "12": [11]
  }
}
```

## Notes

- **CSS only:** No backend files, hooks, services, or npm packages are touched
- **Zero new components:** Only the 8 existing CSS modules and one JSX conditional class addition in `Metrics.tsx`
- **Atomic changes:** Each task targets a single component — git blame stays clean
- **Rollback:** All changes are in CSS files; reverting the branch restores the previous state instantly
- **Preserved behaviour:** All React state, props, animations, and breakpoints that already work correctly are explicitly left unchanged
