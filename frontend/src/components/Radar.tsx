import "./Radar.css";
import Card from "./Common/Card";

const RADAR_RADIUS_PX = 52;
const MAX_ANGLE_DEG = 45;
const MIN_DISTANCE_CM = 20;
const MAX_DISTANCE_CM = 300;

type RadarProps = {
  distanceDisplay: string;
  angleDisplay: string;
  angleDeg: number;
  distanceCm: number;
  faceDetected: boolean;
};

function Radar({ distanceDisplay, angleDisplay, angleDeg, distanceCm, faceDetected }: RadarProps) {
  const clampedAngle = Math.max(-MAX_ANGLE_DEG, Math.min(MAX_ANGLE_DEG, angleDeg));
  const offsetX = (clampedAngle / MAX_ANGLE_DEG) * RADAR_RADIUS_PX;

  const normalised = Math.min(1, Math.max(0,
    (distanceCm - MIN_DISTANCE_CM) / (MAX_DISTANCE_CM - MIN_DISTANCE_CM)
  ));
  const dotOpacity = faceDetected ? 1.0 - normalised * 0.55 : 0.2;

  return (
    <Card title="Radar" accent="green">
      <div className="radar-container">
        {/* SVG radar display */}
        <div className="radar-display">
          <svg viewBox="0 0 120 120" className="radar-svg" aria-hidden="true">
            {/* Rings */}
            <circle cx="60" cy="60" r="54" fill="none" stroke="rgba(34,197,94,0.25)" strokeWidth="1"/>
            <circle cx="60" cy="60" r="36" fill="none" stroke="rgba(34,197,94,0.18)" strokeWidth="1"/>
            <circle cx="60" cy="60" r="18" fill="none" stroke="rgba(34,197,94,0.12)" strokeWidth="1"/>
            {/* Cross-hair */}
            <line x1="60" y1="6"  x2="60" y2="114" stroke="rgba(34,197,94,0.07)" strokeWidth="1"/>
            <line x1="6"  y1="60" x2="114" y2="60" stroke="rgba(34,197,94,0.07)" strokeWidth="1"/>
            {/* Outer ring accent */}
            <circle cx="60" cy="60" r="54" fill="none" stroke="rgba(34,197,94,0.55)" strokeWidth="1.5"
              strokeDasharray="4 6" strokeLinecap="round"/>
          </svg>

          {/* Dot */}
          <div
            className={`radar-dot ${faceDetected ? "radar-dot--active" : ""}`}
            style={{
              transform: `translateX(${offsetX}px)`,
              opacity: dotOpacity,
              transition: "transform 0.25s cubic-bezier(0.4,0,0.2,1), opacity 0.25s ease",
            }}
          />
        </div>

        {/* Info row */}
        <div className="radar-info">
          <div className="radar-stat">
            <span className="radar-stat-label">Distance</span>
            <span className="radar-stat-value">{faceDetected ? distanceDisplay : "—"}</span>
          </div>
          <div className="radar-divider" />
          <div className="radar-stat">
            <span className="radar-stat-label">Angle</span>
            <span className="radar-stat-value">{faceDetected ? angleDisplay : "—"}</span>
          </div>
        </div>
      </div>
    </Card>
  );
}

export default Radar;
