import "./Confidence.css";
import Card from "./Common/Card";

type ConfidenceProps = {
  confidence: number;
};

function Confidence({ confidence }: ConfidenceProps) {
  let status = "Poor";
  let statusClass = "poor";
  let accentColor: "green" | "blue" | "amber" | "rose" = "rose";

  if (confidence >= 90) {
    status = "Excellent";
    statusClass = "excellent";
    accentColor = "green";
  } else if (confidence >= 70) {
    status = "Good";
    statusClass = "good";
    accentColor = "blue";
  } else if (confidence >= 50) {
    status = "Fair";
    statusClass = "fair";
    accentColor = "amber";
  }

  return (
    <Card title="Detection Confidence" accent={accentColor}>
      <div className="confidence-container">
        <div className="confidence-score-row">
          <span className={`confidence-value ${statusClass}`}>{confidence}%</span>
          <span className={`confidence-badge ${statusClass}`}>{status}</span>
        </div>

        <div className="progress-track">
          <div
            className={`progress-fill ${statusClass}`}
            style={{ width: `${confidence}%` }}
            role="progressbar"
            aria-valuenow={confidence}
            aria-valuemin={0}
            aria-valuemax={100}
          />
        </div>

        {/* Tick marks */}
        <div className="progress-ticks" aria-hidden="true">
          <span>0</span>
          <span>50</span>
          <span>100</span>
        </div>
      </div>
    </Card>
  );
}

export default Confidence;
