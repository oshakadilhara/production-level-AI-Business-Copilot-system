import { useState } from "react";
import { Link } from "react-router-dom";
import { queryInsight } from "../api/client";
import { useDataset } from "../context/DatasetContext";

export default function ChatPage() {
  const { datasetId, metadata } = useDataset();
  const [q, setQ] = useState(
    "Why did revenue change in the most recent periods? What should we watch next?"
  );
  const [ctx, setCtx] = useState("");
  const [answer, setAnswer] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function send() {
    if (!datasetId) return;
    setBusy(true);
    setErr(null);
    try {
      const res = await queryInsight({
        dataset_id: datasetId,
        question: q,
        business_context: ctx || undefined,
      });
      setAnswer(res.answer);
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Request failed");
    } finally {
      setBusy(false);
    }
  }

  if (!datasetId) {
    return (
      <div className="page">
        <div className="empty-state">
          <h2>No dataset yet</h2>
          <p className="muted">Upload data before chatting with the copilot.</p>
          <Link className="btn primary" to="/">
            Go to upload
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="page chat-layout">
      <header className="page-header">
        <h1>Copilot chat</h1>
        <p className="muted">
          Hybrid reasoning: Pandas aggregates + row retrieval + OpenAI narrative for{" "}
          <strong>{metadata?.filename}</strong>.
        </p>
      </header>

      <div className="chat-panels">
        <section className="card chat-compose">
          <label className="label">Your question</label>
          <textarea
            className="textarea"
            rows={5}
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Ask about trends, risks, drivers, or next quarter outlook…"
          />
          <label className="label mt">Business context (optional)</label>
          <input
            className="input"
            value={ctx}
            onChange={(e) => setCtx(e.target.value)}
            placeholder="e.g. B2B SaaS, USD, fiscal calendar…"
          />
          <div className="row-end mt">
            <button
              type="button"
              className="btn primary"
              disabled={busy || !q.trim()}
              onClick={() => void send()}
            >
              {busy ? "Thinking…" : "Ask copilot"}
            </button>
          </div>
          {err ? <div className="banner error mt">{err}</div> : null}
        </section>

        <section className="card chat-reply">
          <h2>Insight</h2>
          {answer ? (
            <div className="prose">{answer}</div>
          ) : (
            <p className="muted small">
              Answers combine summary stats and semantically similar rows. Ensure{" "}
              <span className="mono">OPENAI_API_KEY</span> is set on the API server
              for full narrative mode.
            </p>
          )}
        </section>
      </div>
    </div>
  );
}
