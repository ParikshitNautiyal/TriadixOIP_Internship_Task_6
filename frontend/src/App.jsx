import { useCallback, useEffect, useState } from "react";
import "./App.css";
import Library from "./components/Library.jsx";
import ChatPanel from "./components/ChatPanel.jsx";
import TestPanel from "./components/TestPanel.jsx";
import AboutPanel from "./components/AboutPanel.jsx";
import { listDocuments } from "./api/client.js";

const TABS = [
  { id: "ask", label: "Ask questions" },
  { id: "test", label: "Test the system" },
  { id: "about", label: "How it works" },
];

export default function App() {
  const [documents, setDocuments] = useState([]);
  const [chunkCount, setChunkCount] = useState(0);
  const [activeTab, setActiveTab] = useState("ask");

  const refreshDocuments = useCallback(async () => {
    try {
      const data = await listDocuments();
      setDocuments(data.documents);
      setChunkCount(data.chunk_count);
    } catch {
      // Surfaced inline by Library itself on first load failure.
    }
  }, []);

  useEffect(() => {
    refreshDocuments();
  }, [refreshDocuments]);

  return (
    <div className="app">
      <header className="app-header">
        <div className="wordmark">
          <h1>Reading Room</h1>
          <p className="tagline">
            Upload PDFs, Word docs, or slides, then ask questions — every
            answer points back to the page it came from.
          </p>
        </div>
        <p className="status">
          <strong>{documents.length}</strong> document{documents.length === 1 ? "" : "s"} ·{" "}
          <strong>{chunkCount}</strong> chunk{chunkCount === 1 ? "" : "s"} indexed
        </p>
      </header>

      <div className="app-body">
        <Library documents={documents} onChanged={refreshDocuments} />

        <div className="main-pane">
          <nav className="tabs">
            {TABS.map((tab) => (
              <button
                key={tab.id}
                className={`tab-button ${activeTab === tab.id ? "active" : ""}`}
                onClick={() => setActiveTab(tab.id)}
              >
                {tab.label}
              </button>
            ))}
          </nav>

          <div className="tab-panel">
            {activeTab === "ask" && <ChatPanel hasDocuments={documents.length > 0} />}
            {activeTab === "test" && <TestPanel hasDocuments={documents.length > 0} />}
            {activeTab === "about" && <AboutPanel />}
          </div>
        </div>
      </div>
    </div>
  );
}
