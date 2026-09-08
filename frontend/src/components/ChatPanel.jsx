import { useState } from "react";
import { askQuestion } from "../api/client.js";
import SourceList from "./SourceList.jsx";
import "./ChatPanel.css";

export default function ChatPanel({ hasDocuments }) {
  const [history, setHistory] = useState([]); // [{question, answer, sources, grounded}]
  const [question, setQuestion] = useState("");
  const [asking, setAsking] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    const q = question.trim();
    if (!q || asking) return;

    setQuestion("");
    setError(null);
    setAsking(true);
    setHistory((h) => [...h, { question: q, pending: true }]);

    try {
      const result = await askQuestion(q);
      setHistory((h) =>
        h.map((turn, i) =>
          i === h.length - 1 ? { question: q, ...result, pending: false } : turn
        )
      );
    } catch (err) {
      setHistory((h) => h.slice(0, -1));
      setError(err.message);
    } finally {
      setAsking(false);
    }
  }

  return (
    <div className="chat-panel">
      <div className="chat-thread">
        {history.length === 0 && (
          <div className="chat-empty">
            {hasDocuments
              ? "Ask something about what you've uploaded."
              : "Upload at least one document from the Library on the left to get started."}
          </div>
        )}

        {history.map((turn, i) => (
          <div className="chat-turn" key={i}>
            <div className="bubble question">{turn.question}</div>
            {turn.pending ? (
              <div className="bubble answer pending">Searching documents and generating an answer…</div>
            ) : (
              <div className={`bubble answer ${turn.grounded === false ? "ungrounded" : ""}`}>
                <p className="answer-text">{turn.answer}</p>
                <SourceList sources={turn.sources} />
              </div>
            )}
          </div>
        ))}
      </div>

      {error && <p className="chat-error">{error}</p>}

      <form className="chat-composer" onSubmit={handleSubmit}>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder={hasDocuments ? "Ask a question about your documents…" : "Upload a document first…"}
          disabled={!hasDocuments || asking}
        />
        <button type="submit" disabled={!hasDocuments || asking || !question.trim()}>
          Ask
        </button>
      </form>
    </div>
  );
}
