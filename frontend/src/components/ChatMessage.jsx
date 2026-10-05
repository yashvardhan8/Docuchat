import SourceCard from "./SourceCard";

export default function ChatMessage({ role, content, sources }) {
  const isUser = role === "user";

  return (
    <div
      className={`chat-message ${
        isUser ? "chat-message-user" : "chat-message-assistant"
      }`}
    >
      <div className="message-avatar">
        {isUser ? "Y" : "✦"}
      </div>

      <div className="message-content">
        <div className="message-header">
          <span className="chat-role">
            {isUser ? "You" : "DocuChat"}
          </span>
        </div>

        <div className="chat-bubble">
          <p>{content}</p>
        </div>

        {!isUser && sources && sources.length > 0 && (
          <div className="source-list">
            <div className="source-list-header">
              <span>◈</span>
              <span>Sources</span>
            </div>

            <div className="source-list-items">
              {sources.map((s) => (
                <SourceCard key={s.chunk_id} source={s} />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}