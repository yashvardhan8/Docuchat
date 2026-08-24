export default function SourceCard({ source }) {
  return (
    <div className="source-card">
      <span className="source-icon">📄</span>
      <div>
        <div className="source-filename">
          {source.filename}
          {source.page != null && <span className="source-page"> — Page {source.page}</span>}
        </div>
        {source.snippet && <div className="source-snippet">{source.snippet}</div>}
      </div>
    </div>
  );
}
