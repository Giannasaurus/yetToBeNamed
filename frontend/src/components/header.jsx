export default function Header() {
  return (
    <header>
      <p className="hero-kicker">Video-based physics estimation</p>
      <h1>PhysiVision</h1>
      <p className="hero-description">
        Estimate damping and spring constant from ordinary motion videos using computer vision and a damped harmonic oscillator model.
      </p>
      <div className="hero-tags" aria-label="Project highlights">
        <span>No sensors</span>
        <span>OpenCV tracking</span>
        <span>Damped motion fit</span>
      </div>
    </header>
  );
}
