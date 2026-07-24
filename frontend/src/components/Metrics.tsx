import "./Metrics.css";
import Card from "./Common/Card";

type MetricsProps = {
  distance: string;
  angle: string;
  confidence: string;
  fps: string;
  latency: string;
  stability: string;
};

/* Inline SVG icons for each metric row */
function IcoRuler() {
  return <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21.3 15.3a2.4 2.4 0 0 1 0 3.4l-2.6 2.6a2.4 2.4 0 0 1-3.4 0L2.7 8.7a2.4 2.4 0 0 1 0-3.4l2.6-2.6a2.4 2.4 0 0 1 3.4 0Z"/><path d="m14.5 12.5 2-2"/><path d="m11.5 9.5 2-2"/><path d="m8.5 6.5 2-2"/><path d="m17.5 15.5 2-2"/></svg>;
}
function IcoAngle() {
  return <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 21H3"/><path d="M21 21 12 3 3 21"/></svg>;
}
function IcoShield() {
  return <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>;
}
function IcoZap() {
  return <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>;
}
function IcoClock() {
  return <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>;
}
function IcoWave() {
  return <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>;
}

const ROWS: { icon: JSX.Element; label: string; key: keyof MetricsProps }[] = [
  { icon: <IcoRuler  />, label: "Distance",   key: "distance"   },
  { icon: <IcoAngle  />, label: "Angle",      key: "angle"      },
  { icon: <IcoShield />, label: "Confidence", key: "confidence" },
  { icon: <IcoZap    />, label: "FPS",        key: "fps"        },
  { icon: <IcoClock  />, label: "Latency",    key: "latency"    },
  { icon: <IcoWave   />, label: "Stability",  key: "stability"  },
];

function Metrics(props: MetricsProps) {
  return (
    <Card title="Live Metrics" accent="blue">
      <div className="metrics-list">
        {ROWS.map(({ icon, label, key }) => (
          <div className={`metric-row${key === 'distance' ? ' metric-row--primary' : ''}`} key={key}>
            <span className="metric-label">
              <span className="metric-icon" aria-hidden="true">{icon}</span>
              {label}
            </span>
            <span className="metric-value">{props[key]}</span>
          </div>
        ))}
      </div>
    </Card>
  );
}

export default Metrics;
