import React, {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
} from "react";
import type { DatasetMetadata } from "../api/client";

type Ctx = {
  datasetId: string | null;
  metadata: DatasetMetadata | null;
  setDataset: (id: string | null, meta: DatasetMetadata | null) => void;
};

const DatasetContext = createContext<Ctx | undefined>(undefined);

export function DatasetProvider({ children }: { children: React.ReactNode }) {
  const [datasetId, setDatasetId] = useState<string | null>(() => {
    return localStorage.getItem("copilot_dataset_id");
  });
  const [metadata, setMetadata] = useState<DatasetMetadata | null>(() => {
    const raw = localStorage.getItem("copilot_metadata");
    if (!raw) return null;
    try {
      return JSON.parse(raw) as DatasetMetadata;
    } catch {
      return null;
    }
  });

  const setDataset = useCallback(
    (id: string | null, meta: DatasetMetadata | null) => {
      setDatasetId(id);
      setMetadata(meta);
      if (id) localStorage.setItem("copilot_dataset_id", id);
      else localStorage.removeItem("copilot_dataset_id");
      if (meta) localStorage.setItem("copilot_metadata", JSON.stringify(meta));
      else localStorage.removeItem("copilot_metadata");
    },
    []
  );

  const value = useMemo(
    () => ({ datasetId, metadata, setDataset }),
    [datasetId, metadata, setDataset]
  );

  return (
    <DatasetContext.Provider value={value}>{children}</DatasetContext.Provider>
  );
}

export function useDataset() {
  const c = useContext(DatasetContext);
  if (!c) throw new Error("useDataset inside DatasetProvider");
  return c;
}
