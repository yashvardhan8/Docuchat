import { useState, useRef, useEffect } from "react";
import ChatMessage from "./ChatMessage";
import { askQuestion } from "../services/api";

export default function ChatWindow({ hasDocuments }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  async function handleSend() {
    const question = input.trim();

    if (!question || isLoading) return;

    if (!hasDocuments) {
      setError("Upload a document before asking questions.");
      return;
    }

    setError(null);

    const userMsg = {
      role: "user",
      content: question,
    };

    const history = messages.map((m) => ({
      role: m.role,
      content: m.content,
    }));

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);

    try {
      const result = await askQuestion(question, history);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: result.answer,
          sources: result.sources,
        },
      ]);
    } catch (e) {
      setError(e.message);
    } finally {
      setIsLoading(false);
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  function useSuggestion(question) {
    setInput(question);
  }

  return (
    <div className="chat-window">
      <div className="chat-topbar">
        <div>
          <h2>Document Assistant</h2>
          <p>Ask questions and get answers grounded in your documents.</p>
        </div>

        <div className="ai-status">
          <span></span>
          AI Ready
        </div>
      </div>

      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="welcome-screen">
            <div className="welcome-icon">✦</div>

            <h1>
              {hasDocuments
                ? "Ask your documents anything."
                : "Welcome to DocuChat"}
            </h1>

            <p>
              {hasDocuments
                ? "Your documents are ready. Ask a question and I'll find the relevant information."
                : "Upload a PDF or DOCX to start chatting with your documents."}
            </p>

            {hasDocuments && (
              <div className="suggestion-grid">
                <button
                  onClick={() =>
                    useSuggestion("Give me a summary of this document")
                  }
                >
                  <span>✦</span>
                  Summarize this document
                </button>

                <button
                  onClick={() =>
                    useSuggestion("What are the key points in this document?")
                  }
                >
                  <span>⌁</span>
                  Find the key points
                </button>

                <button
                  onClick={() =>
                    useSuggestion(
                      "What are the most important skills mentioned?"
                    )
                  }
                >
                  <span>◈</span>
                  Find important details
                </button>

                <button
                  onClick={() =>
                    useSuggestion("Explain this document in simple words")
                  }
                >
                  <span>✧</span>
                  Explain simply
                </button>
              </div>
            )}
          </div>
        ) : (
          <div className="messages-container">
            {messages.map((m, i) => (
              <ChatMessage
                key={i}
                role={m.role}
                content={m.content}
                sources={m.sources}
              />
            ))}
          </div>
        )}

        {isLoading && (
          <div className="thinking">
            <div className="thinking-avatar">✦</div>

            <div className="thinking-content">
              <span></span>
              <span></span>
              <span></span>
            </div>

            <p>DocuChat is thinking...</p>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {error && <p className="error-text">{error}</p>}

      <div className="chat-input-container">
        <div className="chat-input-row">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              hasDocuments
                ? "Ask anything about your documents..."
                : "Upload a document to start chatting..."
            }
            rows={1}
          />

          <button
            className="send-button"
            onClick={handleSend}
            disabled={isLoading || !input.trim() || !hasDocuments}
          >
            ↑
          </button>
        </div>

        <p className="input-hint">
          Press <strong>Enter</strong> to send ·{" "}
          <strong>Shift + Enter</strong> for a new line
        </p>
      </div>
    </div>
  );
}