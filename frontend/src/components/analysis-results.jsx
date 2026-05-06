import AnalysisCharts from "./analysis-charts.jsx";

function formatNumber(value) {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "N/A";
  }

  return Number(value).toFixed(6);
}

function ResultRow({ label, value }) {
  return (
    <p>
      <span>{label}:</span> {value}
    </p>
  );
}

function ResultSection({ title, rows }) {
  return (
    <section>
      <h3>{title}</h3>
      {rows.map(([label, value]) => (
        <ResultRow key={label} label={label} value={value} />
      ))}
    </section>
  );
}

export default function AnalysisResults({ analysis }) {
  const { physics } = analysis;
  const sections = [
    [
      "RESULTS",
      [
        ["omega", formatNumber(physics.omega)],
        ["omega0", formatNumber(physics.omega0)],
        ["gamma", formatNumber(physics.gamma)],
        ["k", formatNumber(physics.springConstant)],
        ["zeta", formatNumber(physics.zeta)],
        ["phase phi", formatNumber(physics.phase)],
      ],
    ],
    ["REGIME", [["regime", physics.regime]]],
    [
      "STABILITY",
      [
        ["omega drift %", formatNumber(physics.omegaDriftPercent)],
        ["gamma drift %", formatNumber(physics.gammaDriftPercent)],
      ],
    ],
    [
      "FIT",
      [
        ["RMSE", formatNumber(physics.rmse)],
        ["NRMSE", formatNumber(physics.nrmse)],
      ],
    ],
  ];

  return (
    <section className="analysis-results" aria-live="polite">
      {sections.map(([title, rows]) => (
        <ResultSection key={title} title={title} rows={rows} />
      ))}
      <AnalysisCharts series={physics.series} />
    </section>
  );
}
