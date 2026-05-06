export default function AnalysisControls({ mass, onMassChange }) {
  return (
    <div className="analysis-controls">
      <label htmlFor="massInput">Mass (kg)</label>
      <input
        id="massInput"
        min="0"
        step="0.001"
        type="number"
        value={mass}
        onChange={(event) => onMassChange(event.target.value)}
        placeholder="0.250"
      />
    </div>
  );
}
