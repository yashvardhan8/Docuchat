import { deleteDocument } from "../services/api";

export default function DocumentList({ documents, onDeleted }) {
  async function handleDelete(filename) {
    try {
      await deleteDocument(filename);
      onDeleted(filename);
    } catch (e) {
      alert(`Failed to delete: ${e.message}`);
    }
  }

  if (documents.length === 0) {
    return (
      <div className="empty-documents">
        <div className="empty-doc-icon">📄</div>
        <p>No documents yet</p>
        <span>Upload a PDF or DOCX to get started</span>
      </div>
    );
  }

  return (
    <ul className="doc-list">
      {documents.map((doc) => (
        <li key={doc.filename} className="doc-list-item">
          <div className="doc-icon-wrapper">
            <span className="doc-icon">PDF</span>
          </div>

          <div className="doc-info">
            <span className="doc-name" title={doc.filename}>
              {doc.filename}
            </span>

            <span className="doc-meta">
              {doc.chunks} {doc.chunks === 1 ? "chunk" : "chunks"}
            </span>
          </div>

          <button
            className="doc-delete-btn"
            onClick={() => handleDelete(doc.filename)}
            title="Remove document"
            aria-label={`Remove ${doc.filename}`}
          >
            ×
          </button>
        </li>
      ))}
    </ul>
  );
}