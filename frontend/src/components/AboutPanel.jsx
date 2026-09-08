import "./AboutPanel.css";

const STEPS = [
  {
    title: "Upload",
    body: "PDF, Word (.docx), or PowerPoint (.pptx) files come in through the Library panel.",
  },
  {
    title: "Extraction",
    body: "Text is pulled out unit by unit: page-by-page for PDFs, slide-by-slide for PowerPoint (including speaker notes), and section-by-section for Word — honoring manual page breaks when present.",
  },
  {
    title: "Chunking",
    body: "Each unit is split into overlapping ~1000-character chunks so the model gets focused, relevant context instead of whole pages at once.",
  },
  {
    title: "Embedding",
    body: "Every chunk is converted into a vector locally with a Sentence-Transformers model — no network call, no cost.",
  },
  {
    title: "Storage",
    body: "Chunk text, embeddings, and metadata (document name, page number) are stored in a persistent ChromaDB collection.",
  },
  {
    title: "Retrieval",
    body: "Your question is embedded the same way and compared against every stored chunk to find the most semantically similar ones.",
  },
  {
    title: "Generation",
    body: "The retrieved chunks are inserted into a prompt that instructs the model, via the Groq API, to answer only from that context — and to say clearly when the answer isn't there.",
  },
  {
    title: "Citations",
    body: "The document name and page number of every chunk actually used are shown alongside the answer.",
  },
];

export default function AboutPanel() {
  return (
    <div className="about-panel">
      <h2>How the pipeline works</h2>
      <ol className="about-steps">
        {STEPS.map((step) => (
          <li key={step.title}>
            <span className="about-step-title">{step.title}</span>
            <p>{step.body}</p>
          </li>
        ))}
      </ol>

      <div className="about-note">
        <p>
          If nothing retrieved clears the relevance threshold, the app skips
          the model call entirely and returns a "not found" message directly
          — saving a request and avoiding a confident-sounding guess.
        </p>
      </div>
    </div>
  );
}
