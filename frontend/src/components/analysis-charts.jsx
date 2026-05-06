const CHART_WIDTH = 720;
const CHART_HEIGHT = 300;
const CHART_PADDING = 34;

function finiteValues(values) {
  return values.filter((value) => Number.isFinite(value));
}

function domain(values) {
  const cleanValues = finiteValues(values);
  if (cleanValues.length === 0) {
    return [-1, 1];
  }

  let min = Math.min(...cleanValues);
  let max = Math.max(...cleanValues);

  if (min === max) {
    min -= 1;
    max += 1;
  }

  const padding = (max - min) * 0.08;
  return [min - padding, max + padding];
}

function scale(value, min, max, start, end) {
  return start + ((value - min) / (max - min)) * (end - start);
}

function toPoint({ x, y, xDomain, yDomain }) {
  return {
    x: scale(x, xDomain[0], xDomain[1], CHART_PADDING, CHART_WIDTH - CHART_PADDING),
    y: scale(y, yDomain[0], yDomain[1], CHART_HEIGHT - CHART_PADDING, CHART_PADDING),
  };
}

function linePath(points) {
  return points
    .map((point, index) => `${index === 0 ? "M" : "L"} ${point.x.toFixed(2)} ${point.y.toFixed(2)}`)
    .join(" ");
}

function buildSeriesPoints(xValues, yValues, xDomain, yDomain) {
  return xValues
    .map((x, index) => ({ x, y: yValues[index] }))
    .filter((point) => Number.isFinite(point.x) && Number.isFinite(point.y))
    .map((point) => toPoint({ ...point, xDomain, yDomain }));
}

function ChartLegend({ items }) {
  if (!items || items.length === 0) {
    return null;
  }

  return (
    <div className="chart-legend">
      {items.map((item) => (
        <span className="chart-legend-item" key={item.label}>
          <span className={`chart-legend-mark ${item.className}`} />
          {item.label}
        </span>
      ))}
    </div>
  );
}

function ChartFrame({ title, xLabel, yLabel, legend, children }) {
  return (
    <article className="analysis-chart">
      <h3>{title}</h3>
      <ChartLegend items={legend} />
      <svg viewBox={`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`} role="img" aria-label={title}>
        <line className="chart-axis" x1={CHART_PADDING} y1={CHART_HEIGHT - CHART_PADDING} x2={CHART_WIDTH - CHART_PADDING} y2={CHART_HEIGHT - CHART_PADDING} />
        <line className="chart-axis" x1={CHART_PADDING} y1={CHART_PADDING} x2={CHART_PADDING} y2={CHART_HEIGHT - CHART_PADDING} />
        {children}
        <text className="chart-label" x={CHART_WIDTH / 2} y={CHART_HEIGHT - 6} textAnchor="middle">
          {xLabel}
        </text>
        <text className="chart-label" x={12} y={CHART_HEIGHT / 2} textAnchor="middle" transform={`rotate(-90 12 ${CHART_HEIGHT / 2})`}>
          {yLabel}
        </text>
      </svg>
    </article>
  );
}

function MultiLineChart({ title, xLabel, yLabel, xValues, lines }) {
  const xDomain = domain(xValues);
  const yDomain = domain(lines.flatMap((line) => line.values));

  return (
    <ChartFrame
      title={title}
      xLabel={xLabel}
      yLabel={yLabel}
      legend={lines.map((line) => ({ label: line.label, className: line.className }))}
    >
      {lines.map((line) => (
        <path
          className={`chart-line ${line.className}`}
          d={linePath(buildSeriesPoints(xValues, line.values, xDomain, yDomain))}
          key={line.label}
        />
      ))}
    </ChartFrame>
  );
}

function PhaseSpaceChart({ displacement, velocity }) {
  const xDomain = domain(displacement);
  const yDomain = domain(velocity);
  const points = buildSeriesPoints(displacement, velocity, xDomain, yDomain);

  return (
    <ChartFrame title="Phase Space" xLabel="Position" yLabel="Velocity">
      <path className="chart-line chart-line--phase" d={linePath(points)} />
    </ChartFrame>
  );
}

function fitEnvelope(peaks) {
  const validPeaks = peaks.filter((peak) => peak.value > 0);
  if (validPeaks.length < 2) {
    return [];
  }

  const n = validPeaks.length;
  const sumX = validPeaks.reduce((sum, peak) => sum + peak.time, 0);
  const sumY = validPeaks.reduce((sum, peak) => sum + Math.log(peak.value), 0);
  const sumXY = validPeaks.reduce((sum, peak) => sum + peak.time * Math.log(peak.value), 0);
  const sumXX = validPeaks.reduce((sum, peak) => sum + peak.time * peak.time, 0);
  const denominator = n * sumXX - sumX * sumX;

  if (denominator === 0) {
    return [];
  }

  const slope = (n * sumXY - sumX * sumY) / denominator;
  const intercept = (sumY - slope * sumX) / n;

  return validPeaks.map((peak) => ({
    time: peak.time,
    value: Math.exp(intercept + slope * peak.time),
  }));
}

function DampingEnvelopeChart({ peaks }) {
  const envelope = fitEnvelope(peaks);
  const xValues = peaks.map((peak) => peak.time);
  const yValues = [...peaks.map((peak) => peak.value), ...envelope.map((point) => point.value)];
  const xDomain = domain(xValues);
  const yDomain = domain(yValues);
  const envelopePoints = buildSeriesPoints(
    envelope.map((point) => point.time),
    envelope.map((point) => point.value),
    xDomain,
    yDomain,
  );

  return (
    <ChartFrame
      title="Amplitude Decay"
      xLabel="Time (s)"
      yLabel="Amplitude"
      legend={[
        { label: "Peaks", className: "chart-line--primary" },
        { label: "Exponential fit", className: "chart-line--fit" },
      ]}
    >
      {peaks.map((peak) => {
        const point = toPoint({ x: peak.time, y: peak.value, xDomain, yDomain });
        return <circle className="chart-dot" cx={point.x} cy={point.y} r="3" key={`${peak.time}-${peak.value}`} />;
      })}
      {envelopePoints.length > 0 && <path className="chart-line chart-line--fit" d={linePath(envelopePoints)} />}
    </ChartFrame>
  );
}

export default function AnalysisCharts({ series }) {
  return (
    <section className="analysis-charts">
      <MultiLineChart
        title="Spring Motion Fit"
        xLabel="Time (s)"
        yLabel="Position"
        xValues={series.time}
        lines={[
          { label: "Measured signal", values: series.displacement, className: "chart-line--primary" },
          { label: "Model fit", values: series.model, className: "chart-line--fit" },
        ]}
      />
      <MultiLineChart
        title="Mechanical Energy"
        xLabel="Time (s)"
        yLabel="Energy"
        xValues={series.time}
        lines={[{ label: "Energy", values: series.energy, className: "chart-line--energy" }]}
      />
      <PhaseSpaceChart displacement={series.displacement} velocity={series.velocity} />
      <DampingEnvelopeChart peaks={series.peaks} />
    </section>
  );
}
