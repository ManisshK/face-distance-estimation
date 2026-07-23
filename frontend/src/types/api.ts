/**
 * types/api.ts
 *
 * TypeScript interfaces that mirror every FastAPI response shape.
 * These are the single source of truth for all API contracts on
 * the frontend side. No "any" types are used.
 */

// ---------------------------------------------------------------------------
// GET /
// ---------------------------------------------------------------------------

export interface RootResponse {
  application: string;
  version: string;
  status: string;
}

// ---------------------------------------------------------------------------
// GET /health
// ---------------------------------------------------------------------------

export interface HealthResponse {
  status: string;
}

// ---------------------------------------------------------------------------
// GET /frame — three possible shapes
// ---------------------------------------------------------------------------

/** Returned when the camera fails to deliver a frame. */
export interface FrameErrorResponse {
  success: false;
  error: string;
}

/** Returned when the camera works but no face is in the frame. */
export interface FrameNoFaceResponse {
  success: true;
  face_detected: false;
}

/** Bounding box in pixel coordinates. */
export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

/** Returned when a face is successfully detected and measured. */
export interface FrameFaceResponse {
  success: true;
  face_detected: true;
  distance_cm: number;
  angle_deg: number;
  detection_confidence: number;
  bbox: BoundingBox;
}

/** Union of all three possible /frame shapes. */
export type FrameResponse =
  | FrameErrorResponse
  | FrameNoFaceResponse
  | FrameFaceResponse;

// ---------------------------------------------------------------------------
// POST /calibrate
// ---------------------------------------------------------------------------

export interface CalibrationRequest {
  known_distance_cm: number;
}

export interface CalibrationResponse {
  focal_length: number;
}

// ---------------------------------------------------------------------------
// Frontend-derived state (produced by useFrameData, consumed by Dashboard)
// ---------------------------------------------------------------------------

/** Guidance message text shown in the Guidance component. */
export type GuidanceMessage =
  | "Perfect Position"
  | "Move Closer"
  | "Move Back"
  | "Center Face"
  | "Searching for Face";

/** Visual status level tied to guidance. */
export type GuidanceStatus = "success" | "warning" | "error";

/** Stability label derived from confidence history. */
export type StabilityLabel = "Excellent" | "Good" | "Fair" | "Poor";

/**
 * The complete snapshot consumed by Dashboard and its children.
 * All values are ready to display — formatting, conversions and
 * derivations have already been applied.
 */
export interface FrameData {
  /** Whether the backend is reachable. */
  connected: boolean;
  /** Whether a face is currently detected. */
  faceDetected: boolean;
  /** Distance in metres, formatted to 2 decimal places e.g. "1.82 m". */
  distanceDisplay: string;
  /** Raw distance in cm for radar/logic use. */
  distanceCm: number;
  /** Angle in degrees, formatted e.g. "12°". */
  angleDisplay: string;
  /** Raw angle in degrees for radar positioning. */
  angleDeg: number;
  /** Confidence as an integer 0–100 for the Confidence component. */
  confidencePct: number;
  /** Estimated frames per second derived from poll timing. */
  fpsDisplay: string;
  /** Last request round-trip time e.g. "18 ms". */
  latencyDisplay: string;
  /** Human-readable stability label derived from confidence history. */
  stability: StabilityLabel;
  /** Guidance message to display. */
  guidance: GuidanceMessage;
  /** Status level for Guidance component coloring. */
  guidanceStatus: GuidanceStatus;
  /** Last error message, if any. */
  error: string | null;
  /** True while the first request is in-flight. */
  loading: boolean;
  /** Bounding box, present only when faceDetected is true. */
  bbox: BoundingBox | null;
}
