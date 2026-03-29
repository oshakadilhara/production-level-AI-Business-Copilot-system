import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import {
  forecast,
  generateChart,
  getSummary,
  type ChartResponse,
  type PredictionResponse,
  type SummaryResponse,
} from "../api/client";
import ChartPanel from "../components/ChartPanel";
import { useDataset } from "../context/DatasetContext";

export default function DashboardPage() {
  const { datasetId, metadata } = useDataset();
  const [summary, setSummary] = useState<SummaryResponse | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const [xCol, setXCol] = useState("");
  const [yCol, setYCol] = useState("");
  const [chartType, setChartType] = useState<"line" | "bar">("line");
  const [chart, setChart] = useState<ChartResponse | null>(null);

  const [targetCol, setTargetCol] = useState("");
  const [dateCol, setDateCol] = useState("");
  const [horizon, setHorizon] = useState(4);
  const [pred, setPred] = useState<PredictionResponse | null>(null);

  const columns = metadata?.columns ?? [];

  useEffect(() => {
    if (!datasetId) return;
    setLoading(true);
    setErr(null);
    getSummary(datasetId)
      .then(setSummary)
      .catch((e) => setErr(e instanceof Error ? e.message : "Failed to load"))
      .finally(() => setLoading(false));
  }, [datasetId]);

  useEffect(() => {
    if (columns.length && !xCol) setXCol(columns[0]);
    if (columns.length >= 2 && !yCol) setYCol(columns[1]);
    if (columns.length && !targetCol) {
      const numCandidate =
        columns.find((c) =>
          /revenue|sales|amount|total|qty|quantity/i.test(c)
        ) ?? columns[columns.length - 1];
      setTargetCol(numCandidate);
    }
    if (columns.length && !dateCol) {
      const d = columns.find((c) =>
        /date|month|period|time|week|day/i.test(c)
      );
      if (d) setDateCol(d);
    }
  }, [columns, xCol, yCol, targetCol, dateCol]);

  const previewCols = useMemo(() => columns.slice(0, 8), [columns]);

  async function onChart() {
    if (!datasetId || !xCol || !yCol) return;
    setErr(null);
    try {
      const c = await generateChart({
        dataset_id: datasetId,
        x_column: xCol,
        y_column: yCol,
        chart_type: chartType,
      });
      setChart(c);
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Chart failed");
    }
  }

  async function onForecast() {
    if (!datasetId || !targetCol) return;
    setErr(null);
    try {
      const p = await forecast({
        dataset_id: datasetId,
        target_column: targetCol,
        date_column: dateCol || undefined,
        horizon,
      });
      setPred(p);
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Forecast failed");
    }
  }

  if (!datasetId) {
    return (
      <div className="page">
        <div className="empty-state">
          <h2>No dataset yet</h2>
          <p className="muted">Upload a CSV or Excel file to get started.</p>
          <Link className="btn primary" to="/">
            Go to upload
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <header className="page-header row">
        <div>
          <h1>Executive dashboard</h1>
          <p className="muted">
            Summary statistics, interactive charts, and baseline forecasts for{" "}
            <strong>{metadata?.filename}</strong>.
          </p>
        </div>
        <Link className="btn ghost" to="/chat">
          Open copilot chat →
        </Link>
      </header>

      {loading ? <div className="muted">Loading summary…</div> : null}
      {err ? <div className="banner error">{err}</div> : null}

      <section className="card">
        <h2>Dataset snapshot</h2>
        <div className="stat-row">
          <div className="stat">
            <div className="stat-label">Rows</div>
            <div className="stat-value">
              {metadata?.row_count?.toLocaleString() ?? "—"}
            </div>
          </div>
          <div className="stat">
            <div className="stat-label">Columns</div>
            <div className="stat-value">{columns.length}</div>
          </div>
          <div className="stat wide">
            <div className="stat-label">Fields</div>
            <div className="mono small wrap">
              {previewCols.join(", ")}
              {columns.length > previewCols.length ? "…" : ""}
            </div>
          </div>
        </div>
      </section>

      <div className="two-col">
        <section className="card">
          <h2>Visualization</h2>
          <div className="form-grid">
            <label>
              X axis
              <select
                value={xCol}
                onChange={(e) => setXCol(e.target.value)}
                className="select"
              >
                {columns.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Y axis
              <select
                value={yCol}
                onChange={(e) => setYCol(e.target.value)}
                className="select"
              >
                {columns.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Type
              <select
                value={chartType}
                onChange={(e) =>
                  setChartType(e.target.value as "line" | "bar")
                }
                className="select"
              >
                <option value="line">Line</option>
                <option value="bar">Bar</option>
              </select>
            </label>
          </div>
          <button type="button" className="btn primary mt" onClick={() => void onChart()}>
            Generate chart
          </button>
          {chart ? (
            <div className="chart-wrap mt">
              <ChartPanel spec={chart.spec} />
            </div>
          ) : (
            <p className="muted small mt">Configure axes and generate a chart.</p>
          )}
        </section>

        <section className="card">
          <h2>Forecast</h2>
          <p className="small muted">
            Linear regression over a time or row index—useful as a quick baseline, not a full ML stack.
          </p>
          <div className="form-grid">
            <label>
              Target
              <select
                value={targetCol}
                onChange={(e) => setTargetCol(e.target.value)}
                className="select"
              >
                {columns.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Date column (optional)
              <select
                value={dateCol}
                onChange={(e) => setDateCol(e.target.value)}
                className="select"
              >
                <option value="">— row order —</option>
                {columns.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Horizon (periods)
              <input
                type="number"
                min={1}
                max={36}
                value={horizon}
                onChange={(e) => setHorizon(Number(e.target.value))}
                className="input"
              />
            </label>
          </div>
          <button type="button" className="btn primary mt" onClick={() => void onForecast()}>
            Run forecast
          </button>
          {pred ? (
            <div className="table-wrap mt">
              <table className="table">
                <thead>
                  <tr>
                    <th>Step</th>
                    <th>Predicted {pred.target_column}</th>
                  </tr>
                </thead>
                <tbody>
                  {pred.predictions.map((row, i) => (
                    <tr key={i}>
                      <td className="mono">{row.timestamp}</td>
                      <td>{row.predicted_value.toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : null}
        </section>
      </div>

      <section className="card">
        <h2>Summary statistics (Pandas)</h2>
        <p className="small muted">
          Full <span className="mono">describe()</span> payload from the API—scroll
          horizontally if needed.
        </p>
        <pre className="code-block">
          {summary
            ? JSON.stringify(summary.summary_statistics, null, 2)
            : "—"}
        </pre>
      </section>
    </div>
  );
}
