import { useRef } from "react";
import uploadIcon from "../assets/icons/upload.svg";

export default function EmptyUploadPrompt({ isLoadingSample, onSampleSelect, onVideoSelect }) {
  const fileInputRef = useRef(null);

  function openFilePicker() {
    fileInputRef.current.click();
  }

  function handleUploadPromptKeyDown(event) {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      openFilePicker();
    }
  }

  function handleSampleClick(event) {
    event.stopPropagation();
    onSampleSelect();
  }

  return (
    <div
      id="dropzone__clickable"
      role="button"
      tabIndex="0"
      onClick={openFilePicker}
      onKeyDown={handleUploadPromptKeyDown}
    >
      <div id="dropzone__area">
        <img id="uploadIcon" src={uploadIcon} alt="Upload icon" />
        <p>Drag & drop to upload</p>
        <input
          ref={fileInputRef}
          id="uploadFileBtn"
          className="invisible"
          type="file"
          accept="video/*"
          onChange={onVideoSelect}
        />
        <span id="uploadFileLabel">
          Choose File
        </span>
        <button
          id="sample-video-btn"
          type="button"
          onClick={handleSampleClick}
          disabled={isLoadingSample}
        >
          {isLoadingSample ? "Loading sample..." : "Use Sample Video"}
        </button>
      </div>
    </div>
  );
}
