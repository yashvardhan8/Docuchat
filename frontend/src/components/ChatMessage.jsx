import SourceCard from "./SourceCard";

export default function ChatMessage({ role, content, sources }) {
  const isUser = role === "user";
  return (
    <div className={`chat-message ${isUser ? "chat-message-user" : "chat-message-assistant"}`}>
      <div className="chat-bubble">
        <span className="chat-role">{isUser ? "You" : "DocuChat"}</span>
        <p>{content}</p>
      </div>
      {!isUser && sources && sources.length > 0 && (
        <div className="source-list">
          <span className="source-list-label">Sources</span>
          {sources.map((s) => (
            <SourceCard key={s.chunk_id} source={s} />
          ))}
        </div>
      )}
    </div>
  );
}
