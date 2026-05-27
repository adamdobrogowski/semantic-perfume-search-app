import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import SearchPage from './pages/SearchPage';
import DataDashboard from './pages/DataDashboard';
import DevPanel from './pages/DevPanel';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<SearchPage />} />
          <Route path="/dashboard" element={<DataDashboard />} />
          <Route path="/dev" element={<DevPanel />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;