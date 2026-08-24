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
    return <p className="empty-state">No documents uploaded yet.</p>;
  }

  return (
    <ul className="doc-list">
      {documents.map((doc) => (
        <li key={doc.filename} className="doc-list-item">
          <span className="doc-icon">📄</span>
          <div className="doc-info">
            <span className="doc-name">{doc.filename}</span>
            <span className="doc-meta">{doc.chunks} chunks</span>
          </div>
          <button
            className="doc-delete-btn"
            onClick={() => handleDelete(doc.filename)}
            title="Remove document"
          >
            ✕
          </button>
        </li>
      ))}
    </ul>
  );
}
