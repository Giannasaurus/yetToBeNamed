import { useRef, useState } from "react";
import uploadIcon from "../assets/icons/upload.svg";

export default function EmptyUploadPrompt({ onVideoDrop, onVideoSelect }) {
  const [isDragging, setIsDragging] = useState(false);
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

  function handleDragOver(event) {
    event.preventDefault();
    setIsDragging(true);
  }

  function handleDragLeave(event) {
    setIsDragging(false);
  }

  function handleDrop(event) {
    event.preventDefault();
    setIsDragging(false);
    onVideoDrop(event.dataTransfer.files[0]);
  }

  return (
    <div
      id="dropzone__clickable"
      className={isDragging ? "dropzone__clickable--dragging" : ""}
      role="button"
      tabIndex="0"
      onClick={openFilePicker}
      onDragLeave={handleDragLeave}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
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
      </div>
    </div>
  );
}
