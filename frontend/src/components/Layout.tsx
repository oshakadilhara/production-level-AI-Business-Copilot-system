import { NavLink, Outlet } from "react-router-dom";
import { useDataset } from "../context/DatasetContext";

const linkClass = ({ isActive }: { isActive: boolean }) =>
  isActive ? "nav-link active" : "nav-link";

export default function Layout() {
  const { datasetId, metadata } = useDataset();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark" aria-hidden />
          <div>
            <div className="brand-title">AI Business Copilot</div>
            <div className="brand-sub">Mini CFO · Data analyst</div>
          </div>
        </div>
        <nav className="nav">
          <NavLink to="/" end className={linkClass}>
            Upload
          </NavLink>
          <NavLink to="/dashboard" className={linkClass}>
            Dashboard
          </NavLink>
          <NavLink to="/chat" className={linkClass}>
            Chat
          </NavLink>
        </nav>
        <div className="sidebar-foot">
          {datasetId ? (
            <>
              <div className="mono small">Dataset</div>
              <div className="truncate" title={metadata?.filename}>
                {metadata?.filename ?? datasetId.slice(0, 8) + "…"}
              </div>
              <div className="muted small">
                {metadata?.row_count?.toLocaleString() ?? "—"} rows ·{" "}
                {metadata?.columns?.length ?? "—"} cols
              </div>
            </>
          ) : (
            <div className="muted small">Upload a file to unlock analysis.</div>
          )}
        </div>
      </aside>
      <main className="main">
        <Outlet />
      </main>
    </div>
  );
}
