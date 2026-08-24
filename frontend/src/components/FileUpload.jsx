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
        className={`dropzone ${isDragging ? "dropzone-active" : ""}`}
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setIsDragging(false);
          handleFile(e.dataTransfer.files[0]);
        }}
        onClick={() => inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx"
          hidden
          onChange={(e) => handleFile(e.target.files[0])}
        />
        {isUploading ? (
          <p>Uploading & indexing…</p>
        ) : (
          <>
            <p className="dropzone-title">Drop a PDF or DOCX here</p>
            <p className="dropzone-sub">or click to browse</p>
          </>
        )}
      </div>
      {error && <p className="error-text">{error}</p>}
    </div>
  );
}
