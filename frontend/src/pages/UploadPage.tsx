import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { uploadFile } from "../api/client";
import { useDataset } from "../context/DatasetContext";

export default function UploadPage() {
  const { setDataset } = useDataset();
  const nav = useNavigate();
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [drag, setDrag] = useState(false);

  async function onFiles(files: FileList | null) {
    const f = files?.[0];
    if (!f) return;
    setErr(null);
    setBusy(true);
    try {
      const res = await uploadFile(f);
      setDataset(res.dataset_id, res.metadata);
      nav("/dashboard");
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Upload failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="page">
      <header className="page-header">
        <h1>Ingest financial data</h1>
        <p className="muted">
          Upload CSV or Excel. The copilot loads it into a secure analysis
          sandbox, then you can explore summaries, charts, forecasts, and AI
          explanations.
        </p>
      </header>

      <div
        className={`dropzone ${drag ? "drag" : ""}`}
        onDragOver={(e) => {
          e.preventDefault();
          setDrag(true);
        }}
        onDragLeave={() => setDrag(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDrag(false);
          void onFiles(e.dataTransfer.files);
        }}
      >
        <input
          type="file"
          accept=".csv,.xlsx,.xls,text/csv"
          className="file-input"
          id="file"
          disabled={busy}
          onChange={(e) => void onFiles(e.target.files)}
        />
        <label htmlFor="file" className="file-label">
          {busy ? "Uploading…" : "Drop file or click to browse"}
        </label>
        <p className="small muted">
          Supported: <span className="mono">.csv</span>,{" "}
          <span className="mono">.xlsx</span>
        </p>
      </div>

      {err ? <div className="banner error">{err}</div> : null}

      <section className="card grid-info">
        <div>
          <h3>What happens next</h3>
          <ul className="list">
            <li>Pandas profiles columns and summary statistics.</li>
            <li>Optional RAG over rows + LLM narrative for “why” questions.</li>
            <li>Lightweight regression for next-period baselines.</li>
          </ul>
        </div>
        <div className="pill-stack">
          <span className="pill">FastAPI</span>
          <span className="pill">OpenAI</span>
          <span className="pill">FAISS</span>
          <span className="pill">scikit-learn</span>
        </div>
      </section>
    </div>
  );
}
