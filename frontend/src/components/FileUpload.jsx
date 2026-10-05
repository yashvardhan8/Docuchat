import { useState, useRef } from "react";
import { uploadDocument } from "../services/api";

export default function FileUpload({ onUploaded }) {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState(null);
  const inputRef = useRef(null);

  async function handleFile(file) {
    if (!file) return;

    setError(null);
    setIsUploading(true);

    try {
      const result = await uploadDocument(file);
      onUploaded(result);
    } catch (e) {
      setError(e.message);
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <div>
      <div
        className={`dropzone ${isDragging ? "dropzone-active" : ""} ${
          isUploading ? "dropzone-uploading" : ""
        }`}
        onDragOver={(e) => {
          e.preventDefault();
          if (!isUploading) setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setIsDragging(false);

          if (!isUploading) {
            handleFile(e.dataTransfer.files[0]);
          }
        }}
        onClick={() => {
          if (!isUploading) {
            inputRef.current?.click();
          }
        }}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx"
          hidden
          onChange={(e) => {
            handleFile(e.target.files[0]);
            e.target.value = "";
          }}
        />

        {isUploading ? (
          <>
            <div className="upload-icon uploading-icon">
              <span></span>
            </div>

            <p className="dropzone-title">
              Processing document...
            </p>

            <p className="dropzone-sub">
              Uploading and creating your document index
            </p>
          </>
        ) : (
          <>
            <div className="upload-icon">
              <span>↑</span>
            </div>

            <p className="dropzone-title">
              Upload a document
            </p>

            <p className="dropzone-sub">
              Drag & drop or click to browse
            </p>

            <div className="supported-files">
              <span>PDF</span>
              <span>DOCX</span>
            </div>
          </>
        )}
      </div>

      {error && <p className="error-text">{error}</p>}
    </div>
  );
}