import { useEffect, useRef, useState } from "react";
import AnalysisControls from "./analysis-controls.jsx";
import AnalysisResults from "./analysis-results.jsx";
import DropzoneActions from "./dropzone-actions.jsx";
import EmptyUploadPrompt from "./empty-upload-prompt.jsx";
import VideoPreview from "./video-preview.jsx";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export default function Dropzone() {
  const [selectedVideo, setSelectedVideo] = useState(null);
  const [videoUrl, setVideoUrl] = useState(null);
  const [mass, setMass] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const replaceFileInputRef = useRef(null);
  const parsedMass = Number(mass);
  const hasVideo = Boolean(videoUrl);
  const isAnalyzeDisabled = isAnalyzing || parsedMass <= 0;

  function handleReplaceFileClick() {
    replaceFileInputRef.current.click();
  }

  function handleVideoSelect(event) {
    const video = event.target.files[0];

    if (video) {
      const url = URL.createObjectURL(video);
      setSelectedVideo(video);
      setVideoUrl(url);
      setAnalysis(null);
      setError("");
    }
  }

  async function handleAnalyze() {
    if (!selectedVideo || isAnalyzeDisabled) {
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedVideo);
    formData.append("mass", parsedMass);

    setIsAnalyzing(true);
    setError("");
    setAnalysis(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/analyze`, {
        method: "POST",
        body: formData,
      });

      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.detail || "Analysis failed.");
      }

      setAnalysis(payload);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsAnalyzing(false);
    }
  }

  useEffect(() => {
    return () => {
      if (videoUrl) {
        URL.revokeObjectURL(videoUrl);
      }
    };
  }, [videoUrl]);

  return (
    <main>
      <div id="dropzone">
        {hasVideo && <VideoPreview videoUrl={videoUrl} />}

        {!hasVideo && <EmptyUploadPrompt onVideoSelect={handleVideoSelect} />}

        {hasVideo && <AnalysisControls mass={mass} onMassChange={setMass} />}

        {hasVideo && (
          <DropzoneActions
            isAnalyzing={isAnalyzing}
            isAnalyzeDisabled={isAnalyzeDisabled}
            onAnalyze={handleAnalyze}
            onReplaceClick={handleReplaceFileClick}
            onVideoSelect={handleVideoSelect}
            replaceFileInputRef={replaceFileInputRef}
          />
        )}

        {error && <p className="analysis-message analysis-message--error">{error}</p>}

        {analysis && <AnalysisResults analysis={analysis} />}
      </div>
    </main>
  );
}
