const rawBase = import.meta.env.VITE_API_URL ?? "";

export function apiUrl(path: string): string {
  const p = path.startsWith("/") ? path : `/${path}`;
  if (!rawBase) return p;
  return `${rawBase.replace(/\/$/, "")}${p}`;
}

export async function apiJson<T>(
  path: string,
  init?: RequestInit
): Promise<T> {
  const res = await fetch(apiUrl(path), {
    ...init,
    headers: {
      Accept: "application/json",
      ...(init?.headers ?? {}),
    },
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      if (body?.detail) detail = String(body.detail);
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

export type DatasetMetadata = {
  filename: string;
  columns: string[];
  row_count: number;
};

export type UploadResponse = {
  dataset_id: string;
  metadata: DatasetMetadata;
};

export type SummaryResponse = {
  dataset_id: string;
  metadata: DatasetMetadata;
  summary_statistics: Record<string, unknown>;
  time_grain: string | null;
};

export type InsightResponse = {
  answer: string;
  supporting_facts: Record<string, unknown>;
};

export type PredictionResponse = {
  dataset_id: string;
  target_column: string;
  predictions: { timestamp: string; predicted_value: number }[];
};

export type ChartSpec = {
  type: string;
  data: {
    labels: string[];
    datasets: {
      label: string;
      data: number[];
      borderColor?: string;
      backgroundColor?: string;
    }[];
  };
  options?: Record<string, unknown>;
};

export type ChartResponse = {
  dataset_id: string;
  spec: ChartSpec;
};

export async function uploadFile(file: File): Promise<UploadResponse> {
  const fd = new FormData();
  fd.append("file", file);
  return apiJson<UploadResponse>("/api/files/upload", {
    method: "POST",
    body: fd,
  });
}

export function getSummary(datasetId: string) {
  return apiJson<SummaryResponse>(`/api/datasets/${datasetId}/summary`);
}

export function queryInsight(body: {
  dataset_id: string;
  question: string;
  business_context?: string;
}) {
  return apiJson<InsightResponse>("/api/insights/query", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export function forecast(body: {
  dataset_id: string;
  target_column: string;
  date_column?: string;
  horizon: number;
}) {
  return apiJson<PredictionResponse>("/api/predictions/forecast", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export function generateChart(body: {
  dataset_id: string;
  x_column: string;
  y_column: string;
  chart_type: string;
}) {
  return apiJson<ChartResponse>("/api/charts/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}
