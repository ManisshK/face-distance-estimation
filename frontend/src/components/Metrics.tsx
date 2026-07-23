import "./Metrics.css";
import Card from "./Common/Card";

type MetricsProps = {
  distance: string;
  angle: string;
  confidence: string;
  fps: string;
  latency: string;
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