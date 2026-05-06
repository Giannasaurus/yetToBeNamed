export default function DropzoneActions({
  isAnalyzing,
  isAnalyzeDisabled,
  onAnalyze,
  onReplaceClick,
  onVideoSelect,
  replaceFileInputRef,
}) {
  return (
    <footer id="dropzone__btnGroup">
      <button
        id="replace-file-btn"
        type="button"
        onClick={onReplaceClick}
        disabled={isAnalyzing}
      >
        Replace File
      </button>
      <input
        ref={replaceFileInputRef}
        className="invisible"
        type="file"
        accept="video/*"
        onChange={onVideoSelect}
      />
      <button
        id="upload-analyze-btn"
        type="button"
        onClick={onAnalyze}
        disabled={isAnalyzeDisabled}
      >
        {isAnalyzing ? "Analyzing..." : "Upload & Analyze"}
      </button>
    </footer>
  );
}
