import { useRef, useState } from "react";
import { clearDocuments, uploadDocuments } from "../api/client.js";
import "./Library.css";

export default function Library({ documents, onChanged }) {
  const [pending, setPending] = useState(false);
  const [log, setLog] = useState([]); // [{filename, status, detail}]
  const [dragOver, setDragOver] = useState(false);
  const [clearing, setClearing] = useState(false);
  const inputRef = useRef(null);

  async function handleFiles(fileList) {
    const files = Array.from(fileList || []);
    if (files.length === 0) return;
    setPending(true);
    setLog([]);
    try {
      const result = await uploadDocuments(files);
      setLog(result.results);
      onChanged();
    } catch (err) {
      setLog([{ filename: "Upload", status: "error", detail: err.message }]);
    } finally {
      setPending(false);
    }
  }

  async function handleClear() {
    if (!window.confirm("Clear the entire library? This removes every indexed document.")) return;
    setClearing(true);
    try {
      await clearDocuments();
      setLog([]);
      onChanged();
    } catch (err) {
      setLog([{ filename: "Clear library", status: "error", detail: err.message }]);
    } finally {
      setClearing(false);
    }
  }

  return (
    <aside className="library">
      <div>
        <h2 className="library-heading">Library</h2>
        <p className="library-sub">PDF, Word (.docx), or PowerPoint (.pptx)</p>
      </div>

      <div
        className={`dropzone ${dragOver ? "drag-over" : ""} ${pending ? "busy" : ""}`}
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragOver(false);
          handleFiles(e.dataTransfer.files);
        }}
        onClick={() => !pending && inputRef.current?.click()}
        role="button"
        tabIndex={0}
      >
        <input
          ref={inputRef}
          type="file"
          multiple
          accept=".pdf,.docx,.pptx"
          hidden
          onChange={(e) => handleFiles(e.target.files)}
        />
        {pending ? (
          <span>Processing…</span>
        ) : (
          <span>
            Drop files here, or <span className="dropzone-link">browse</span>
          </span>
        )}
      </div>

      {log.length > 0 && (
        <ul className="upload-log">
          {log.map((item, i) => (
            <li key={i} className={`upload-log-item status-${item.status}`}>
              <span className="filename">{item.filename}</span>
              <span className="detail">{item.detail}</span>
            </li>
          ))}
        </ul>
      )}

      <div className="shelf">
        <h3 className="shelf-heading">
          On the shelf {documents.length > 0 && <span className="mono">({documents.length})</span>}
        </h3>
        {documents.length === 0 ? (
          <p className="shelf-empty">Nothing here yet — upload a document to begin.</p>
        ) : (
          <ul className="shelf-list">
            {documents.map((name) => (
              <li key={name}>{name}</li>
            ))}
          </ul>
        )}
      </div>

      {documents.length > 0 && (
        <button className="clear-button" onClick={handleClear} disabled={clearing}>
          {clearing ? "Clearing…" : "Clear library"}
        </button>
      )}
    </aside>
  );
}
