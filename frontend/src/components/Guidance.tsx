/**
 * Guidance.tsx
 *
 * Pure presentational component. No logic changes from original.
 * message and status are derived upstream in useFrameData.
 */

import "./Guidance.css";
import Card from "./Common/Card";

type GuidanceProps = {
  message: string;
  status: "success" | "warning" | "error";
};

function Guidance({ message, status }: GuidanceProps) {
  return (
    <Card title="🧭 Guidance">
      <div className="guidance-container">
        <div className={`guidance-icon ${status}`}>
          {status === "success" ? "✅" : status === "warning" ? "⚠️" : "❌"}
        </div>

        <h3>{message}</h3>

        <p>
          Follow the guidance to achieve the best face position for accurate
          distance estimation.
        </p>
      </div>
    </Card>
  );
}

export default Guidance;
