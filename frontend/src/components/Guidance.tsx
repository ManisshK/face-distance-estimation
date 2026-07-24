import "./Guidance.css";
import Card from "./Common/Card";

type GuidanceProps = {
  message: string;
  status: "success" | "warning" | "error";
};

function IcoCheck() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="20 6 9 17 4 12"/>
    </svg>
  );
}
function IcoArrowUp() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <line x1="12" y1="19" x2="12" y2="5"/><polyline points="5 12 12 5 19 12"/>
    </svg>
  );
}
function IcoArrowDown() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <line x1="12" y1="5" x2="12" y2="19"/><polyline points="19 12 12 19 5 12"/>
    </svg>
  );
}
function IcoArrowRight() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>
    </svg>
  );
}
function IcoSearch() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
    </svg>
  );
}

function getIcon(message: string, status: string) {
  if (message === "Perfect Position") return <IcoCheck />;
  if (message === "Move Back")        return <IcoArrowDown />;
  if (message === "Move Closer")      return <IcoArrowUp />;
  if (message === "Center Face")      return <IcoArrowRight />;
  if (status === "error")             return <IcoSearch />;
  return <IcoSearch />;
}

const accentMap = {
  success: "green",
  warning: "amber",
  error:   "rose",
} as const;

function Guidance({ message, status }: GuidanceProps) {
  return (
    <Card title="Guidance" accent={accentMap[status]}>
      <div className="guidance-container">
        <div className={`guidance-icon-wrap ${status}`}>
          {getIcon(message, status)}
        </div>
        <div className="guidance-text">
          <h3 className="guidance-message">{message}</h3>
          <p className="guidance-hint">
            Adjust your position for optimal face detection accuracy.
          </p>
        </div>
      </div>
    </Card>
  );
}

export default Guidance;
