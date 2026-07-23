/**
 * CalibrationPanel.tsx
 *
 * Allows the user to trigger a single-frame focal-length calibration.
 *
 * Workflow:
 *  1. User enters the known distance (cm) to the camera.
 *  2. User clicks "Calibrate".
 *  3. POST /calibrate is called via the api service.
 *  4. On success: the returned focal_length is displayed.
 *  5. On failure: a meaningful error message is shown.
 *
 * This component manages only its own local form state — no global
 * state is touched.
 */

import { useState } from "react";
import { calibrate } from "../services/api";
import Card from "./Common/Card";
import "./CalibrationPanel.css";

/** Minimum sensible distance for calibration in centimetres. */
const MIN_DISTANCE_CM = 10;

/** Maximum sensible distance for calibration in centimetres. */
const MAX_DISTANCE_CM = 500;

function CalibrationPanel() {
  const [distanceInput, setDistanceInput] = useState<string>("");
  const [focalLength, setFocalLength] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /** Parse and validate the user's distance input. */
  function parseDistance(): number | null {
    const value = parseFloat(distanceInput);
    if (isNaN(value) || value < MIN_DISTANCE_CM || value > MAX_DISTANCE_CM) {
      return null;
    }
    return value;
  }

  async function handleCalibrate() {
    setError(null);
    setFocalLength(null);

    const distance = parseDistance();
    if (distance === null) {
      setError(
        `Please enter a valid distance between ${MIN_DISTANCE_CM} and ${MAX_DISTANCE_CM} cm.`
      );
      return;
    }

    setIsLoading(true);
    try {
      const result = await calibrate(distance);
      setFocalLength(result.focal_length);
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Calibration failed.";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }

  const inputValid =
    distanceInput !== "" && parseDistance() !== null;

  return (
    <Card title="🔧 Calibration">
      <div className="calibration-container">
        <p className="calibration-description">
          Stand at a known distance from the camera and enter it below,
          then click Calibrate to update the focal length.
        </p>

        <div className="calibration-input-row">
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

          <button
            className={`calibration-button ${isLoading ? "loading" : ""}`}
            onClick={handleCalibrate}
            disabled={isLoading || !inputValid}
            aria-busy={isLoading}
          >
            {isLoading ? "Calibrating…" : "Calibrate"}
          </button>
        </div>

        {/* Success result */}
        {focalLength !== null && (
          <div className="calibration-result success">
            ✅ Focal length: <strong>{focalLength.toFixed(2)} px</strong>
          </div>
        )}

        {/* Error message */}
        {error !== null && (
          <div className="calibration-result error">
            ❌ {error}
          </div>
        )}
      </div>
    </Card>
  );
}

export default CalibrationPanel;
