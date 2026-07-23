/**
 * Dashboard.tsx
 *
 * Application shell and sole owner of live backend state.
 *
 * Data flow:
 *   useFrameData() → FrameData snapshot → props → child components
 *
 * The camera section renders the live MJPEG stream from GET /video
 * when the backend is reachable. An overlay is shown on top of the
 * stream (or instead of it) when the backend is offline or loading.
 */

import Metrics from "./Metrics";
import Confidence from "./Confidence";
import Radar from "./Radar";
import Guidance from "./Guidance";
import CalibrationPanel from "./CalibrationPanel";
import { useFrameData } from "../hooks/useFrameData";
import { getVideoStreamUrl } from "../services/api";
import "./Dashboard.css";

function Dashboard() {
  const {
    connected,
    faceDetected,
    distanceDisplay,
    distanceCm,
    angleDisplay,
    angleDeg,
    confidencePct,
    fpsDisplay,
    latencyDisplay,
    stability,
    guidance,
    guidanceStatus,
    error,
    loading,
  } = useFrameData();

  // Track whether the <img> has successfully loaded at least one frame.
  // NOTE: onLoad never fires for MJPEG streams because the response never
  // "finishes" — the browser keeps the connection open indefinitely.
  // Stream visibility is therefore driven by `connected` (from /frame poll)
  // rather than by an onLoad event. The <img> is always mounted so the
  // browser opens the stream connection immediately on render.

  // -------------------------------------------------------------------------
  // Header badge
  // -------------------------------------------------------------------------

  let badgeClass = "header-badge";
  let badgeText = "⚪ CONNECTING";

  if (loading) {
    badgeClass = "header-badge connecting";
    badgeText = "⚪ CONNECTING";
  } else if (!connected) {
    badgeClass = "header-badge error-badge";
    badgeText = "🔴 OFFLINE";
  } else if (!faceDetected) {
    badgeClass = "header-badge warning-badge";
    badgeText = "🟡 NO FACE";
  } else {
    badgeClass = "header-badge success";
    badgeText = "🟢 READY";
  }

  // -------------------------------------------------------------------------
  // Camera overlay — shown when backend is unreachable or still loading.
  // Hidden (via CSS) once the stream is live.
  // -------------------------------------------------------------------------

  let cameraIcon = "📷";
  let cameraTitle = "LIVE CAMERA";
  let cameraMessage: string;

  if (loading) {
    cameraMessage = "Connecting to backend…";
  } else if (!connected) {
    cameraIcon = "⚠️";
    cameraMessage = error ?? "Cannot reach backend. Is the server running?";
  } else {
    cameraMessage = "Starting stream…";
  }

  // Show the overlay only when the backend is genuinely unreachable.
  // When connected, the <img> is visible and the overlay is not rendered.
  // The "Starting stream…" intermediate state is removed — if the backend
  // is reachable the stream is already playing.
  const showOverlay = !connected;

  // -------------------------------------------------------------------------
  // Render
  // -------------------------------------------------------------------------

  const videoUrl = getVideoStreamUrl();

  return (
    <div className="dashboard">

      {/* ── HEADER ─────────────────────────────────────────────────────── */}
      <header className="dashboard-header">

        <div className="header-left">
          <h1>🎯 Face Distance Estimation</h1>
          <p>AI Powered Face Monitoring System</p>
        </div>

        <div className="header-right">

          <div className={badgeClass}>
            {badgeText}
          </div>

          <div className="header-info">
            <span>FPS</span>
            <strong>{fpsDisplay}</strong>
          </div>

          <div className="header-info">
            <span>Latency</span>
            <strong>{latencyDisplay}</strong>
          </div>

        </div>

      </header>

      {/* ── MAIN GRID ──────────────────────────────────────────────────── */}
      <main className="dashboard-grid">

        {/* CAMERA SECTION */}
        <section className="camera-section">
          <div className="camera-window">

            {/*
              Live MJPEG stream.
              The <img> tag natively supports MJPEG — the browser keeps one
              HTTP connection open and repaints as new JPEG frames arrive.
              onLoad is NOT used here because MJPEG responses never complete,
              so that event never fires. Visibility is controlled by the
              `connected` flag from the /frame polling hook instead.
              The image is always mounted; CSS handles show/hide.
            */}
            <img
              src={videoUrl}
              alt="Live webcam feed with face detection overlay"
              className={`camera-stream ${connected ? "camera-stream--visible" : ""}`}
            />

            {/* Status overlay — sits on top when stream hasn't loaded */}
            {showOverlay && (
              <div className="camera-overlay">
                <div className="camera-icon">{cameraIcon}</div>
                <h2>{cameraTitle}</h2>
                <p>{cameraMessage}</p>
              </div>
            )}

          </div>
        </section>

        {/* RIGHT PANEL */}
        <aside className="right-panel">

          <Metrics
            distance={distanceDisplay}
            angle={angleDisplay}
            confidence={`${confidencePct}%`}
            fps={fpsDisplay}
            latency={latencyDisplay}
            stability={stability}
          />

          <Confidence confidence={confidencePct} />

          <Radar
            distanceDisplay={distanceDisplay}
            angleDisplay={angleDisplay}
            angleDeg={angleDeg}
            distanceCm={distanceCm}
            faceDetected={faceDetected}
          />

          <Guidance
            message={guidance}
            status={guidanceStatus}
          />

          <CalibrationPanel />

        </aside>

      </main>

    </div>
  );
}

export default Dashboard;
