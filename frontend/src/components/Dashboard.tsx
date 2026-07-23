/**
 * Dashboard.tsx
 *
 * Application shell and sole owner of live backend state.
 *
 * Data flow:
 *   useFrameData() → FrameData snapshot → props → child components
 *
 * Responsibilities:
 *  - Call useFrameData() once.
 *  - Pass derived values down to presentational children.
 *  - Render the camera section with connection-aware overlay text.
 *  - Render the header with live FPS, latency and connection badge.
 *
 * No business logic or derivations live here — everything comes
 * pre-computed from the hook.
 */

import Metrics from "./Metrics";
import Confidence from "./Confidence";
import Radar from "./Radar";
import Guidance from "./Guidance";
import CalibrationPanel from "./CalibrationPanel";
import { useFrameData } from "../hooks/useFrameData";
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
  // Camera overlay content
  // -------------------------------------------------------------------------

  let cameraIcon = "📷";
  let cameraTitle = "LIVE CAMERA";
  let cameraMessage: string;

  if (loading) {
    cameraMessage = "Connecting to backend…";
  } else if (!connected) {
    cameraIcon = "⚠️";
    cameraMessage = error ?? "Cannot reach backend. Is the server running?";
  } else if (!faceDetected) {
    cameraMessage = "No face detected. Position yourself in front of the camera.";
  } else {
    cameraMessage = "Face detected — tracking active.";
  }

  // -------------------------------------------------------------------------
  // Render
  // -------------------------------------------------------------------------

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
            <div className="camera-overlay">

              <div className="camera-icon">
                {cameraIcon}
              </div>

              <h2>{cameraTitle}</h2>

              <p>{cameraMessage}</p>

            </div>
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
