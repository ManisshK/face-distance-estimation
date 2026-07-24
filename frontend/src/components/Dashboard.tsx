/**
 * Dashboard.tsx — application shell.
 * Owns live state via useFrameData(), passes values to presentational children.
 * Zero business logic lives here.
 */

import Metrics from "./Metrics";
import Confidence from "./Confidence";
import Radar from "./Radar";
import Guidance from "./Guidance";
import CalibrationPanel from "./CalibrationPanel";
import { useFrameData } from "../hooks/useFrameData";
import { getVideoStreamUrl } from "../services/api";
import "./Dashboard.css";

/* ── Inline SVG icon helpers (no external dependency) ───────────────────── */

function IconCamera() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
      <circle cx="12" cy="13" r="4"/>
    </svg>
  );
}

function IconWifi() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <line x1="1" y1="1" x2="23" y2="23"/>
      <path d="M16.72 11.06A10.94 10.94 0 0 1 19 12.55"/>
      <path d="M5 12.55a10.94 10.94 0 0 1 5.17-2.39"/>
      <path d="M10.71 5.05A16 16 0 0 1 22.56 9"/>
      <path d="M1.42 9a15.91 15.91 0 0 1 4.7-2.88"/>
      <path d="M8.53 16.11a6 6 0 0 1 6.95 0"/>
      <line x1="12" y1="20" x2="12.01" y2="20"/>
    </svg>
  );
}

function IconBrain() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none"
      stroke="white" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96-.46 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.44-4.14"/>
      <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96-.46 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.44-4.14"/>
    </svg>
  );
}

/* ─────────────────────────────────────────────────────────────────────────── */

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

  /* ── Header badge ─────────────────────────────────────────────────────── */

  let badgeClass = "header-badge connecting";
  let badgeLabel = "Connecting";

  if (loading) {
    badgeClass = "header-badge connecting";
    badgeLabel = "Connecting";
  } else if (!connected) {
    badgeClass = "header-badge error-badge";
    badgeLabel = "Offline";
  } else if (!faceDetected) {
    badgeClass = "header-badge warning-badge";
    badgeLabel = "No Face";
  } else {
    badgeClass = "header-badge success";
    badgeLabel = "Ready";
  }

  /* ── Camera overlay ───────────────────────────────────────────────────── */

  const showOverlay = !connected;

  let overlayIcon = <IconCamera />;
  let overlayTitle = "Live Camera";
  let overlayMessage = "Connecting to backend…";

  if (!loading && !connected) {
    overlayIcon = <IconWifi />;
    overlayTitle = "No Connection";
    overlayMessage = error ?? "Cannot reach backend. Is the server running?";
  }

  const videoUrl = getVideoStreamUrl();

  /* ── Render ───────────────────────────────────────────────────────────── */

  return (
    <div className="dashboard">

      {/* ══ HEADER ══════════════════════════════════════════════════════════ */}
      <header className="dashboard-header">

        <div className="header-left">
          {/* Logo mark */}
          <div className="header-logo" aria-hidden="true">
            <IconBrain />
          </div>
          <div className="header-brand">
            <h1>Face Distance Estimation</h1>
            <p>AI Powered Face Monitoring System</p>
          </div>
        </div>

        <div className="header-right">

          {/* Animated status badge */}
          <div className={badgeClass} role="status" aria-live="polite">
            <span className="badge-dot" aria-hidden="true" />
            {badgeLabel}
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

      {/* ══ MAIN GRID ═══════════════════════════════════════════════════════ */}
      <main className="dashboard-grid">

        {/* CAMERA */}
        <section className="camera-section">
          <div className="camera-window">

            <img
              src={videoUrl}
              alt="Live webcam feed with face detection overlay"
              className={`camera-stream ${connected ? "camera-stream--visible" : ""}`}
            />

            {showOverlay && (
              <div className="camera-overlay">
                <div className="camera-icon" style={{ color: connected ? "#4ade80" : "#94a3b8" }}>
                  {overlayIcon}
                </div>
                <h2>{overlayTitle}</h2>
                <p>{overlayMessage}</p>
              </div>
            )}

          </div>
        </section>

        {/* SIDEBAR */}
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
