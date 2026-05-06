function ResultMetric({ label, value }) {
  return (
    <div>
      <dt>{label}</dt>
      <dd>{value}</dd>
    </div>
  );
}

export default function AnalysisResults({ analysis }) {
  const metrics = [
    ["Samples", analysis.samples],
    ["FPS", analysis.fps.toFixed(2)],
    ["dt", `${analysis.dt.toFixed(4)}s`],
    ["Regime", analysis.physics.regime],
    ["k", analysis.physics.springConstant.toFixed(3)],
    ["Damping", analysis.physics.gamma.toFixed(3)],
    ["omega0", analysis.physics.omega0.toFixed(3)],
    ["NRMSE", analysis.physics.nrmse.toFixed(3)],
    ["Peaks", analysis.physics.peakCount],
  ];

  return (
    <section className="analysis-results" aria-live="polite">
      <h2>Tracking Results</h2>
      <dl>
        {metrics.map(([label, value]) => (
          <ResultMetric key={label} label={label} value={value} />
        ))}
      </dl>
    </section>
  );
}
