function formatPercent(value) {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "unavailable";
  }

  return `${Number(value).toFixed(2)}%`;
}

function dampingDescription(zeta) {
  if (zeta < 0.05) {
    return "The spring is only lightly damped, so it keeps oscillating with little loss per cycle.";
  }

  if (zeta < 0.2) {
    return "The spring is underdamped with a visible but gradual loss of amplitude.";
  }

  if (zeta < 1) {
    return "The spring is underdamped, but damping is strong enough to noticeably shrink each swing.";
  }

  return "The motion is heavily damped, so it returns toward rest without sustained oscillation.";
}

function fitDescription(nrmse) {
  if (nrmse < 0.08) {
    return "The model follows the tracked motion closely.";
  }

  if (nrmse < 0.18) {
    return "The model captures the overall motion, though some frame-level tracking noise remains.";
  }

  return "The model fit is loose, so the video may need cleaner tracking or a more stable view.";
}

function stabilityDescription(omegaDriftPercent, gammaDriftPercent) {
  if (omegaDriftPercent === null || gammaDriftPercent === null) {
    return "Stability could not be fully estimated from the available peaks.";
  }

  if (omegaDriftPercent < 10 && gammaDriftPercent < 25) {
    return "Frequency and damping stay fairly consistent across the recording.";
  }

  return "The motion changes across the recording, so the spring behavior is not perfectly steady.";
}

export default function AnalysisSummary({ physics }) {
  const energySpread = physics.energy.max - physics.energy.min;
  const energySpreadLabel = Number.isFinite(energySpread) ? energySpread.toFixed(3) : "N/A";

  return (
    <section className="analysis-summary">
      <h3>Spring Behavior</h3>
      <p>
        This looks <span>{physics.regime.toLowerCase()}</span>. {dampingDescription(physics.zeta)}
      </p>
      <p>{fitDescription(physics.nrmse)}</p>
      <p>{stabilityDescription(physics.omegaDriftPercent, physics.gammaDriftPercent)}</p>
      <ul>
        <li>
          Damping ratio: <span>{physics.zeta.toFixed(4)}</span>
        </li>
        <li>
          Frequency drift: <span>{formatPercent(physics.omegaDriftPercent)}</span>
        </li>
        <li>
          Damping drift: <span>{formatPercent(physics.gammaDriftPercent)}</span>
        </li>
        <li>
          Energy spread: <span>{energySpreadLabel}</span>
        </li>
      </ul>
    </section>
  );
}
