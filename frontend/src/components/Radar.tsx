/**
 * Radar.tsx
 *
 * Pure presentational component.
 *
 * The radar dot position reflects the live horizontal angle:
 *   - Centred at 0°
 *   - Moves left for negative angles (face to the left)
 *   - Moves right for positive angles (face to the right)
 *
 * The dot opacity scales with distance — closer faces produce a
 * brighter dot, far faces a dimmer one — giving a subtle depth cue
 * without adding visual clutter.
 *
 * Props use raw numeric values so positioning math stays in this
 * component where it belongs.
 */

import "./Radar.css";
import Card from "./Common/Card";

/** Half-width of the radar circle in pixels, used for dot offset calculation. */
const RADAR_RADIUS_PX = 70;

/** Maximum angle mapped to the radar edge (matches backend MAX_ANGLE_DISPLAY_DEG). */
const MAX_ANGLE_DEG = 45;

/** Distance range (cm) used to scale dot opacity. */
const MIN_DISTANCE_CM = 20;
const MAX_DISTANCE_CM = 300;

type RadarProps = {
  /** Formatted distance string shown in the info row, e.g. "1.82 m" */
  distanceDisplay: string;
  /** Formatted angle string shown in the info row, e.g. "12.0°" */
  angleDisplay: string;
  /** Raw angle in degrees for dot positioning (-45 … +45) */
  angleDeg: number;
  /** Raw distance in cm for dot opacity scaling */
  distanceCm: number;
  /** Whether a face is currently detected */
  faceDetected: boolean;
};

function Radar({
  distanceDisplay,
  angleDisplay,
  angleDeg,
  distanceCm,
  faceDetected,
}: RadarProps) {
  // Clamp angle to [-MAX, +MAX] before mapping to pixels.
  const clampedAngle = Math.max(-MAX_ANGLE_DEG, Math.min(MAX_ANGLE_DEG, angleDeg));

  // Linear mapping: angle → horizontal offset from centre.
  const offsetX = (clampedAngle / MAX_ANGLE_DEG) * RADAR_RADIUS_PX;

  // Dot opacity: full opacity when close, half opacity when far.
  const normalised = Math.min(
    1,
    Math.max(
      0,
      (distanceCm - MIN_DISTANCE_CM) / (MAX_DISTANCE_CM - MIN_DISTANCE_CM)
    )
  );
  // Invert: close (normalised ≈ 0) → opacity 1.0; far (normalised ≈ 1) → opacity 0.4
  const dotOpacity = faceDetected ? 1.0 - normalised * 0.6 : 0.25;

  return (
    <Card title="📡 Radar">
      <div className="radar-container">
        <div className="radar-circle">
          {/* Dot positioned by inline style; CSS handles base appearance */}
          <div
            className="radar-dot"
            style={{
              transform: `translateX(${offsetX}px)`,
              opacity: dotOpacity,
              transition: "transform 0.2s ease, opacity 0.2s ease",
            }}
          />
        </div>

        <div className="radar-info">
          <p>
            <strong>Distance:</strong> {faceDetected ? distanceDisplay : "—"}
          </p>
          <p>
            <strong>Angle:</strong> {faceDetected ? angleDisplay : "—"}
          </p>
        </div>
      </div>
    </Card>
  );
}

export default Radar;
