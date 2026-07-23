/**
 * hooks/useFrameData.ts
 *
 * Custom hook that polls GET /frame at a configurable interval and derives
 * all values needed by the Dashboard and its child components.
 *
 * Responsibilities:
 *  - Runs the polling loop with setInterval.
 *  - Measures round-trip latency per request.
 *  - Estimates frames per second from actual poll timing.
 *  - Maintains a short confidence history for stability calculation.
 *  - Derives guidance message, guidance status, and stability label.
 *  - Manages connected / loading / error states.
 *  - Cleans up the interval on unmount to prevent memory leaks.
 *
 * Returns a single FrameData snapshot; Dashboard passes sub-values
 * straight to its presentational children.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { fetchFrame } from "../services/api";
import type {
  BoundingBox,
  FrameData,
  GuidanceMessage,
  GuidanceStatus,
  StabilityLabel,
} from "../types/api";

// ---------------------------------------------------------------------------
// Thresholds — all distances in centimetres
// ---------------------------------------------------------------------------

/** Below this distance the subject is too close. */
const DISTANCE_TOO_CLOSE_CM = 40;

/** Above this distance the subject is too far. */
const DISTANCE_TOO_FAR_CM = 150;

/** Absolute angle (degrees) beyond which the face is considered off-centre. */
const ANGLE_CENTRE_THRESHOLD_DEG = 10;

/** Number of recent confidence samples used for the stability calculation. */
const STABILITY_WINDOW = 10;

/** Default polling interval in milliseconds. */
const DEFAULT_INTERVAL_MS = 200;

// ---------------------------------------------------------------------------
// Pure derivation helpers (no React — easy to unit-test)
// ---------------------------------------------------------------------------

/**
 * Convert a distance in centimetres to a display string in metres.
 * e.g. 182.4 → "1.82 m"
 */
function formatDistanceM(cm: number): string {
  return `${(cm / 100).toFixed(2)} m`;
}

/**
 * Format an angle in degrees for display.
 * e.g. -12.7 → "-12.7°"
 */
function formatAngleDeg(deg: number): string {
  return `${deg.toFixed(1)}°`;
}

/**
 * Derive the guidance message and status from the current measurements.
 * Priority: face missing > too close > too far > off-centre > perfect.
 */
function deriveGuidance(
  faceDetected: boolean,
  distanceCm: number,
  angleDeg: number
): { guidance: GuidanceMessage; guidanceStatus: GuidanceStatus } {
  if (!faceDetected) {
    return { guidance: "Searching for Face", guidanceStatus: "error" };
  }
  if (distanceCm < DISTANCE_TOO_CLOSE_CM) {
    return { guidance: "Move Back", guidanceStatus: "warning" };
  }
  if (distanceCm > DISTANCE_TOO_FAR_CM) {
    return { guidance: "Move Closer", guidanceStatus: "warning" };
  }
  if (Math.abs(angleDeg) > ANGLE_CENTRE_THRESHOLD_DEG) {
    return { guidance: "Center Face", guidanceStatus: "warning" };
  }
  return { guidance: "Perfect Position", guidanceStatus: "success" };
}

/**
 * Derive a stability label from a window of recent confidence values.
 * Uses the mean of the window to match the Confidence component's thresholds.
 */
function deriveStability(history: number[]): StabilityLabel {
  if (history.length === 0) return "Poor";
  const mean = history.reduce((a, b) => a + b, 0) / history.length;
  if (mean >= 90) return "Excellent";
  if (mean >= 70) return "Good";
  if (mean >= 50) return "Fair";
  return "Poor";
}

// ---------------------------------------------------------------------------
// Initial state
// ---------------------------------------------------------------------------

const INITIAL_STATE: FrameData = {
  connected: false,
  faceDetected: false,
  distanceDisplay: "— m",
  distanceCm: 0,
  angleDisplay: "—°",
  angleDeg: 0,
  confidencePct: 0,
  fpsDisplay: "—",
  latencyDisplay: "— ms",
  stability: "Poor",
  guidance: "Searching for Face",
  guidanceStatus: "error",
  error: null,
  loading: true,
  bbox: null,
};

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

/**
 * Poll the backend /frame endpoint and return a live FrameData snapshot.
 *
 * @param intervalMs  How often to poll in milliseconds (default 200 ms → ~5 fps).
 *                    Lower values produce smoother updates but increase CPU and
 *                    network usage.
 */
export function useFrameData(intervalMs: number = DEFAULT_INTERVAL_MS): FrameData {
  const [data, setData] = useState<FrameData>(INITIAL_STATE);

  // Rolling confidence history for stability calculation.
  const confidenceHistoryRef = useRef<number[]>([]);

  // Timestamps for FPS estimation.
  const lastSuccessfulPollRef = useRef<number | null>(null);

  // Guards against state updates on an unmounted component.
  const mountedRef = useRef(true);

  const poll = useCallback(async () => {
    const requestStart = performance.now();

    try {
      const frame = await fetchFrame();
      const requestEnd = performance.now();

      if (!mountedRef.current) return;

      const latencyMs = Math.round(requestEnd - requestStart);

      // FPS: derived from time between successful responses.
      let fps = "—";
      const now = requestEnd;
      if (lastSuccessfulPollRef.current !== null) {
        const elapsed = now - lastSuccessfulPollRef.current;
        if (elapsed > 0) {
          fps = (1000 / elapsed).toFixed(1);
        }
      }
      lastSuccessfulPollRef.current = now;

      // --- Handle frame error (camera failed to capture) ---
      if (!frame.success) {
        setData((prev) => ({
          ...prev,
          connected: true,
          faceDetected: false,
          loading: false,
          error: frame.error,
          guidance: "Searching for Face",
          guidanceStatus: "error",
          fpsDisplay: fps,
          latencyDisplay: `${latencyMs} ms`,
        }));
        return;
      }

      // --- Handle no face ---
      if (!frame.face_detected) {
        const { guidance, guidanceStatus } = deriveGuidance(false, 0, 0);
        setData((prev) => ({
          ...prev,
          connected: true,
          faceDetected: false,
          loading: false,
          error: null,
          guidance,
          guidanceStatus,
          fpsDisplay: fps,
          latencyDisplay: `${latencyMs} ms`,
          bbox: null,
        }));
        return;
      }

      // --- Handle successful face detection ---
      const { distance_cm, angle_deg, detection_confidence, bbox } = frame;

      // Convert confidence from [0,1] to [0,100] integer.
      const confidencePct = Math.round(detection_confidence * 100);

      // Update rolling confidence history.
      const history = confidenceHistoryRef.current;
      history.push(confidencePct);
      if (history.length > STABILITY_WINDOW) {
        history.shift();
      }

      const stability = deriveStability(history);
      const { guidance, guidanceStatus } = deriveGuidance(
        true,
        distance_cm,
        angle_deg
      );

      const newBbox: BoundingBox = { ...bbox };

      setData({
        connected: true,
        faceDetected: true,
        distanceDisplay: formatDistanceM(distance_cm),
        distanceCm: distance_cm,
        angleDisplay: formatAngleDeg(angle_deg),
        angleDeg: angle_deg,
        confidencePct,
        fpsDisplay: fps,
        latencyDisplay: `${latencyMs} ms`,
        stability,
        guidance,
        guidanceStatus,
        error: null,
        loading: false,
        bbox: newBbox,
      });
    } catch (err: unknown) {
      if (!mountedRef.current) return;

      const message =
        err instanceof Error ? err.message : "Unknown connection error.";

      setData((prev) => ({
        ...prev,
        connected: false,
        faceDetected: false,
        loading: false,
        error: message,
        guidance: "Searching for Face",
        guidanceStatus: "error",
      }));
    }
  }, []);

  useEffect(() => {
    mountedRef.current = true;

    // Fire immediately so the first update doesn't wait a full interval.
    void poll();

    const intervalId = setInterval(() => {
      void poll();
    }, intervalMs);

    return () => {
      mountedRef.current = false;
      clearInterval(intervalId);
    };
  }, [poll, intervalMs]);

  return data;
}
