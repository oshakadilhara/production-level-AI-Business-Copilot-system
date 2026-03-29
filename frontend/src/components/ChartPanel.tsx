import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Line, Bar } from "react-chartjs-2";
import type { ChartSpec } from "../api/client";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

export default function ChartPanel({ spec }: { spec: ChartSpec }) {
  if (spec.type === "bar") {
    return <Bar data={spec.data} options={spec.options as object} />;
  }
  return <Line data={spec.data} options={spec.options as object} />;
}
