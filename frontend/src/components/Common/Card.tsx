import "./Card.css";

type CardProps = {
  title: string;
  children: React.ReactNode;
  /** Optional accent colour for the left border stripe */
  accent?: "blue" | "green" | "amber" | "rose" | "none";
};

function Card({ title, children, accent = "none" }: CardProps) {
  return (
    <div className={`card card--accent-${accent}`}>
      <h2 className="card-title">{title}</h2>
      <div className="card-body">{children}</div>
    </div>
  );
}

export default Card;
