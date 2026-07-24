import { useState } from "react";
import { calibrate } from "../services/api";
import Card from "./Common/Card";
import "./CalibrationPanel.css";

const MIN_DISTANCE_CM = 10;
const MAX_DISTANCE_CM = 500;

function IcoTarget() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10"/>
      <circle cx="12" cy="12" r="6"/>
      <circle cx="12" cy="12" r="2"/>
    </svg>
  );
}

function IcoLoader() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"
      className="spin">
      <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
    </svg>
  );
}

function CalibrationPanel() {
  const [distanceInput, setDistanceInput] = useState<string>("");
  const [focalLength, setFocalLength]     = useState<number | null>(null);
  const [isLoading, setIsLoading]         = useState(false);
  const [error, setError]                 = useState<string | null>(null);

  function parseDistance(): number | null {
    const value = parseFloat(distanceInput);
    if (isNaN(value) || value < MIN_DISTANCE_CM || value > MAX_DISTANCE_CM) return null;
    return value;
  }

  async function handleCalibrate() {
    setError(null);
    setFocalLength(null);
    const distance = parseDistance();
    if (distance === null) {
      setError(`Enter a distance between ${MIN_DISTANCE_CM}–${MAX_DISTANCE_CM} cm.`);
      return;
    }
    setIsLoading(true);
    try {
      const result = await calibrate(distance);
      setFocalLength(result.focal_length);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Calibration failed.");
    } finally {
      setIsLoading(false);
    }
  }

  const inputValid = distanceInput !== "" && parseDistance() !== null;

  return (
    <Card title="Calibration" accent="none">
      <div className="calibration-container">
        <p className="calibration-description">
          Stand at a known distance, enter it below, then calibrate.
        </p>

        <div className="calibration-input-row">
          <div className="calibration-input-wrap">
            <input
              type="number"
              className="calibration-input"
              placeholder="Distance (cm)"
              min={MIN_DISTANCE_CM}
              max={MAX_DISTANCE_CM}
              step="1"
              value={distanceInput}
              onChange={(e) => {
                setDistanceInput(e.target.value);
                setError(null);
                setFocalLength(null);
              }}
              disabled={isLoading}
              aria-label="Known distance in centimetres"
            />
            <span className="calibration-input-unit">cm</span>
          </div>

          <button
            className={`calibration-button ${isLoading ? "loading" : ""}`}
            onClick={handleCalibrate}
            disabled={isLoading || !inputValid}
            aria-busy={isLoading}
          >
            {isLoading ? (
              <><IcoLoader /> Calibrating</>
            ) : (
              <><IcoTarget /> Calibrate</>
            )}
          </button>
        </div>

        {focalLength !== null && (
          <div className="calibration-result success">
            <span className="cal-result-label">Focal length</span>
            <span className="cal-result-value">{focalLength.toFixed(1)} px</span>
          </div>
        )}

        {error !== null && (
          <div className="calibration-result error">
            {error}
          </div>
        )}
      </div>
    </Card>
  );
}

export default CalibrationPanel;
