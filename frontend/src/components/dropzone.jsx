// import { useState } from 'react'
import { useRef } from 'react'
import uploadIcon from '../assets/icons/upload.svg'

export default function Dropzone() {
    const replaceFileInputRef = useRef(null)

    function handleReplaceFileClick() {
        replaceFileInputRef.current.click()
    }

    return (
        <main>
            <div id="dropzone">
                <div id="dropzone__area">
                    <img id="uploadIcon" src={uploadIcon} alt="Upload icon" />
                    <p>Drag & drop to upload</p>
                    <input id="uploadFileBtn" className="invisible" type="file" />
                    <label id="uploadFileLabel" htmlFor="uploadFileBtn">Choose File</label>
                </div>
                <footer id="dropzone__btnGroup">
                    <button id="replace-file-btn" type="button" onClick={handleReplaceFileClick}>Replace File</button>
                    <input ref={replaceFileInputRef} className="invisible" type="file" />
                    <button id="upload-analyze-btn" type="submit">Upload & Analyze</button>
                </footer>
            </div>
        </main>
    )
}
