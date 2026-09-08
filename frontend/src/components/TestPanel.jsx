import { useEffect, useState } from "react";
import { getDefaultTestQuestions, runTestSuite } from "../api/client.js";
import SourceList from "./SourceList.jsx";
import "./TestPanel.css";

export default function TestPanel({ hasDocuments }) {
  const [questionsText, setQuestionsText] = useState("");
  const [running, setRunning] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    getDefaultTestQuestions()
      .then((d) => setQuestionsText(d.questions.join("\n")))
      .catch(() => {});
  }, []);

  async function handleRun() {
    const questions = questionsText.split("\n").map((q) => q.trim()).filter(Boolean);
    if (questions.length === 0) return;
    setRunning(true);
    setError(null);
    setResults(null);
    try {
      const data = await runTestSuite(questions);
      setResults(data.results);
    } catch (err) {
      setError(err.message);
    } finally {
      setRunning(false);
    }
  }

  return (
    <div className="test-panel">
      <p className="test-intro">
        Run a batch of questions through retrieval and generation to
        sanity-check semantic search, grounding, and citation correctness.
      </p>

      <label className="test-label" htmlFor="test-questions">
        Test questions (one per line)
      </label>
      <textarea
        id="test-questions"
        value={questionsText}
        onChange={(e) => setQuestionsText(e.target.value)}
        rows={6}
        disabled={!hasDocuments}
      />

      <button className="run-button" onClick={handleRun} disabled={!hasDocuments || running}>
        {running ? "Running…" : "Run tests"}
      </button>

      {!hasDocuments && <p className="test-hint">Upload a document before running tests.</p>}
      {error && <p className="test-error">{error}</p>}

      {results && (
        <ul className="test-results">
          {results.map((r, i) => (
            <li key={i} className={`test-result ${r.grounded ? "grounded" : "ungrounded"}`}>
              <div className="test-result-header">
                <span className="test-status">{r.grounded ? "Grounded" : "Not found / ungrounded"}</span>
                <span className="test-question">{r.question}</span>
              </div>
              <div className="test-result-body">
                <p className="test-meta">
                  <span className="mono">{r.num_chunks_retrieved}</span> chunk(s) retrieved
                  {r.top_distance != null && (
                    <>
                      {" "}
                      · best match distance <span className="mono">{r.top_distance}</span> (lower = more similar)
                    </>
                  )}
                </p>
                <p className="answer-text">{r.answer}</p>
                <SourceList sources={r.sources} />
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
