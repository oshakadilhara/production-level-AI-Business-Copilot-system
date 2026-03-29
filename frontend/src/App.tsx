import { Route, Routes, Navigate } from "react-router-dom";
import { DatasetProvider } from "./context/DatasetContext";
import Layout from "./components/Layout";
import UploadPage from "./pages/UploadPage";
import DashboardPage from "./pages/DashboardPage";
import ChatPage from "./pages/ChatPage";

export default function App() {
  return (
    <DatasetProvider>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<UploadPage />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="chat" element={<ChatPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </DatasetProvider>
  );
}
