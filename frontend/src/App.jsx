import { useState, useEffect } from "react";
import FileUpload from "./components/FileUpload";
import DocumentList from "./components/DocumentList";
import ChatWindow from "./components/ChatWindow";
import { listDocuments } from "./services/api";

export default function App() {
  const [documents, setDocuments] = useState([]);
  const [loadError, setLoadError] = useState(null);

  async function refreshDocuments() {
    try {
      const result = await listDocuments();
      setDocuments(result.documents);
    } catch (e) {
      setLoadError(e.message);
    }
  }

  useEffect(() => {
    refreshDocuments();
  }, []);

  function handleUploaded() {
    refreshDocuments();
  }

  function handleDeleted(filename) {
    setDocuments((prev) => prev.filter((d) => d.filename !== filename));
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <h1>DocuChat</h1>
        <p className="app-subtitle">Ask questions about your documents, grounded in retrieval.</p>
      </header>

      <div className="app-body">
        <aside className="sidebar">
          <h2>Upload Documents</h2>
          <FileUpload onUploaded={handleUploaded} />
          <h2>Your Documents</h2>
          {loadError && <p className="error-text">{loadError}</p>}
          <DocumentList documents={documents} onDeleted={handleDeleted} />
        </aside>

        <main className="chat-area">
          <ChatWindow hasDocuments={documents.length > 0} />
        </main>
      </div>
    </div>
  );
}
