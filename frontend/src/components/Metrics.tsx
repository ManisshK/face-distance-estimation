/**
 * Metrics.tsx
 *
 * Pure presentational component. Displays the six live metric rows.
 * All formatting is done upstream in useFrameData — this component
 * only renders what it receives.
 */

import "./Metrics.css";
import Card from "./Common/Card";

type MetricsProps = {
  /** Formatted distance string, e.g. "1.82 m" */
  distance: string;
  /** Formatted angle string, e.g. "12.0°" */
  angle: string;
  /** Formatted confidence string, e.g. "96%" */
  confidence: string;
  /** Estimated FPS string, e.g. "4.8" */
  fps: string;
  /** Round-trip latency string, e.g. "18 ms" */
  latency: string;
  /** Human-readable stability label */
  stability: string;
};

function Metrics({
  distance,
  angle,
  confidence,
  fps,
  latency,
  stability,
}: MetricsProps) {
  return (
    <Card title="📊 Live Metrics">
      <div className="metric-row">
        <span>Distance</span>
        <span>{distance}</span>
      </div>

      <div className="metric-row">
        <span>Angle</span>
        <span>{angle}</span>
      </div>

      <div className="metric-row">
        <span>Confidence</span>
        <span>{confidence}</span>
      </div>

      <div className="metric-row">
        <span>FPS</span>
        <span>{fps}</span>
      </div>

      <div className="metric-row">
        <span>Latency</span>
        <span>{latency}</span>
      </div>

      <div className="metric-row">
        <span>Stability</span>
        <span>{stability}</span>
      </div>
    </Card>
  );
}

export default Metrics;
