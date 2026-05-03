import { Routes, Route, Navigate } from 'react-router-dom';
import AppLayout from './components/AppLayout';
import WorkbenchPage from './pages/WorkbenchPage';
import HistoryPage from './pages/HistoryPage';
import ComparePage from './pages/ComparePage';
import DomainConfigPage from './pages/DomainConfigPage';
import ModelManagePage from './pages/ModelManagePage';

function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<Navigate to="/workbench" replace />} />
        <Route path="/workbench" element={<WorkbenchPage />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/compare" element={<ComparePage />} />
        <Route path="/domains" element={<DomainConfigPage />} />
        <Route path="/models" element={<ModelManagePage />} />
      </Route>
    </Routes>
  );
}

export default App;
