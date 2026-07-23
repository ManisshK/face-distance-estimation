import { useState } from "react";
import Metrics from "./Metrics";
import Confidence from "./Confidence";
import Radar from "./Radar";
import Guidance from "./Guidance";
import "./Dashboard.css";

function Dashboard() {
  const [distance] = useState("1.82 m");
  const [angle] = useState("12°");
  const [confidence] = useState(96);

  const [fps] = useState("32");
  const [latency] = useState("18 ms");
  const [stability] = useState("Excellent");

  const [guidance] = useState("Perfect Position");
  const [status] =
    useState<"success" | "warning" | "error">("success");

  return (
    <div className="dashboard">

      {/* HEADER */}
      <header className="dashboard-header">

        <div className="header-left">
          <h1>🎯 Face Distance Estimation</h1>
          <p>AI Powered Face Monitoring System</p>
        </div>

        <div className="header-right">

          <div className="header-badge success">
            🟢 READY
          </div>

          <div className="header-info">
            <span>FPS</span>
            <strong>{fps}</strong>
          </div>

          <div className="header-info">
            <span>Latency</span>
            <strong>{latency}</strong>
          </div>

        </div>

      </header>

      <main className="dashboard-grid">

        {/* CAMERA */}

        <section className="camera-section">

          <div className="camera-window">

            <div className="camera-overlay">

              <div className="camera-icon">
                📷
              </div>

              <h2>LIVE CAMERA</h2>

              <p>Waiting for backend connection...</p>

            </div>

          </div>

        </section>

        {/* RIGHT PANEL */}

        <aside className="right-panel">

          <Metrics
            distance={distance}
            angle={angle}
            confidence={`${confidence}%`}
            fps={fps}
            latency={latency}
            stability={stability}
          />

          <Confidence confidence={confidence} />

          <Radar
            distance={distance}
            angle={angle}
          />

          <Guidance
            message={guidance}
            status={status}
          />

        </aside>

      </main>

    </div>
  );
}

export default Dashboard;