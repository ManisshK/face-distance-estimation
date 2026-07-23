/**
 * services/api.ts
 *
 * Centralised API communication layer.
 *
 * Responsibilities:
 *  - All fetch() calls live here — never in components or hooks directly.
 *  - Base URL is read from VITE_API_BASE_URL (falls back to localhost:8000).
 *  - Every function returns a typed promise.
 *  - HTTP errors and network errors are converted into thrown Error objects
 *    so callers can catch a single error type.
 *
 * Usage:
 *   import { fetchFrame, calibrate } from "@/services/api";
 */

import type {
  CalibrationRequest,
  CalibrationResponse,
  FrameResponse,
  HealthResponse,
  RootResponse,
} from "../types/api";

// ---------------------------------------------------------------------------
// Base URL
// ---------------------------------------------------------------------------

/**
 * The backend origin.
 * Set VITE_API_BASE_URL in your .env file to override.
 * Example:  VITE_API_BASE_URL=http://localhost:8000
 */
const BASE_URL: string =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ??
  "http://localhost:8000";

// ---------------------------------------------------------------------------
// Request timeout
// ---------------------------------------------------------------------------

/** Maximum milliseconds to wait for any single request before aborting. */
const REQUEST_TIMEOUT_MS = 5_000;

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

/**
 * Perform a fetch with an AbortController-based timeout.
 * Throws on network error, timeout, or non-2xx HTTP status.
 */
async function request<T>(
  path: string,
  init: RequestInit = {}
): Promise<T> {
  const controller = new AbortController();
  const timerId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const response = await fetch(`${BASE_URL}${path}`, {
      ...init,
      signal: controller.signal,
    });

    if (!response.ok) {
      // Surface the backend error message when available.
      let detail = `HTTP ${response.status}`;
      try {
        const body = (await response.json()) as { detail?: string };
        if (body.detail) detail = body.detail;
      } catch {
        // ignore — keep the generic HTTP status message
      }
      throw new Error(detail);
    }

    return (await response.json()) as T;
  } catch (err: unknown) {
    if (err instanceof Error && err.name === "AbortError") {
      throw new Error("Request timed out. Is the backend running?");
    }
    throw err;
  } finally {
    clearTimeout(timerId);
  }
}

// ---------------------------------------------------------------------------
// Public API functions
// ---------------------------------------------------------------------------

/**
 * GET /
 * Returns application name, version and running status.
 */
export async function fetchRoot(): Promise<RootResponse> {
  return request<RootResponse>("/");
}

/**
 * GET /health
 * Lightweight liveness probe — use this to check backend reachability.
 */
export async function fetchHealth(): Promise<HealthResponse> {
  return request<HealthResponse>("/health");
}

/**
 * GET /frame
 * Captures one frame, runs face detection and estimation, returns results.
 * This is the primary endpoint polled at the configured refresh interval.
 */
export async function fetchFrame(): Promise<FrameResponse> {
  return request<FrameResponse>("/frame");
}

/**
 * POST /calibrate
 * Triggers a single-frame focal-length calibration at the given distance.
 *
 * @param known_distance_cm  Physical distance in centimetres at which the
 *                           subject is positioned during calibration.
 * @throws Error             If no face is detected, distance is invalid, or
 *                           the backend returns a non-2xx status.
 */
export async function calibrate(
  known_distance_cm: number
): Promise<CalibrationResponse> {
  const body: CalibrationRequest = { known_distance_cm };
  return request<CalibrationResponse>("/calibrate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}
