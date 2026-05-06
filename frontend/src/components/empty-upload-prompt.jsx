import uploadIcon from "../assets/icons/upload.svg";

export default function EmptyUploadPrompt({ onVideoSelect }) {
  return (
    <label id="dropzone__clickable" htmlFor="uploadFileBtn">
      <div id="dropzone__area">
        <img id="uploadIcon" src={uploadIcon} alt="Upload icon" />
        <p>Drag & drop to upload</p>
        <input
          id="uploadFileBtn"
          className="invisible"
          type="file"
          accept="video/*"
          onChange={onVideoSelect}
        />
        <label id="uploadFileLabel" htmlFor="uploadFileBtn">
          Choose File
        </label>
      </div>
    </label>
  );
}
