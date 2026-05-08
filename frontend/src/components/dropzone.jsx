import { useEffect, useRef, useState } from "react";
import AnalysisControls from "./analysis-controls.jsx";
import AnalysisResults from "./analysis-results.jsx";
import DropzoneActions from "./dropzone-actions.jsx";
import EmptyUploadPrompt from "./empty-upload-prompt.jsx";
import VideoPreview from "./video-preview.jsx";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
const MASS_TO_KG = {
  kg: 1,
  g: 0.001,
  lb: 0.45359237,
  oz: 0.028349523125,
};

export default function Dropzone() {
  const [selectedVideo, setSelectedVideo] = useState(null);
  const [videoUrl, setVideoUrl] = useState(null);
  const [mass, setMass] = useState("");
  const [massUnit, setMassUnit] = useState("kg");
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const replaceFileInputRef = useRef(null);
  const parsedMass = Number(mass);
  const massInKg = parsedMass * MASS_TO_KG[massUnit];
  const hasVideo = Boolean(videoUrl);
  const isAnalyzeDisabled = isAnalyzing || !Number.isFinite(massInKg) || massInKg <= 0;

  function handleReplaceFileClick() {
    replaceFileInputRef.current.click();
  }

  function selectVideo(video) {
    if (!video) {
      return;
    }

    if (!video.type.startsWith("video/")) {
      setError("Please upload a video file.");
      return;
    }

    const url = URL.createObjectURL(video);
    setSelectedVideo(video);
    setVideoUrl(url);
    setAnalysis(null);
    setError("");
  }

  function handleVideoSelect(event) {
    selectVideo(event.target.files[0]);
    event.target.value = "";
  }

  async function handleAnalyze() {
    if (!selectedVideo || isAnalyzeDisabled) {
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedVideo);
    formData.append("mass", massInKg);

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

        {!hasVideo && (
          <EmptyUploadPrompt
            onVideoDrop={selectVideo}
            onVideoSelect={handleVideoSelect}
          />
        )}

        {hasVideo && (
          <AnalysisControls
            mass={mass}
            massUnit={massUnit}
            onAnalyze={handleAnalyze}
            onMassChange={setMass}
            onMassUnitChange={setMassUnit}
            isAnalyzeDisabled={isAnalyzeDisabled}
          />
        )}

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
