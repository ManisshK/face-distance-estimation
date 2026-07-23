import "./Confidence.css";
import Card from "./Common/Card";

type ConfidenceProps = {
  confidence: number;
};

function Confidence({ confidence }: ConfidenceProps) {
  let status = "Poor";
  let statusClass = "poor";

  if (confidence >= 90) {
    status = "Excellent";
    statusClass = "excellent";
  } else if (confidence >= 70) {
    status = "Good";
    statusClass = "good";
  } else if (confidence >= 50) {
    status = "Fair";
    statusClass = "fair";
  }

  return (
    <Card title="🎯 Detection Confidence">
      <div className="confidence-container">
        <h1 className="confidence-value">{confidence}%</h1>

        <p className={`confidence-status ${statusClass}`}>
          {status}
        </p>

        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{ width: `${confidence}%` }}
          ></div>
        </div>
      </div>
    </Card>
  );
}

export default Confidence;