import "./Radar.css";
import Card from "./Common/Card";

type RadarProps = {
  distance: string;
  angle: string;
};

function Radar({ distance, angle }: RadarProps) {
  return (
    <Card title="📡 Radar">
      <div className="radar-container">
        <div className="radar-circle">
          <div className="radar-dot"></div>
        </div>

        <div className="radar-info">
          <p><strong>Distance:</strong> {distance}</p>
          <p><strong>Angle:</strong> {angle}</p>
        </div>
      </div>
    </Card>
  );
}

export default Radar;