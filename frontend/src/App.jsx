import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import SegmentationPage from './SegmentationPage';
import LoanRiskPage from './LoanRiskPage';
import FeeOptimizationPage from './FeeOptimizationPage';
import ForexSimulatorPage from './ForexSimulatorPage';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <nav className="navbar">
          <h1>NCBA Revenue Maximizer</h1>
          <ul>
            <li><Link to="/">Dashboard</Link></li>
            <li><Link to="/segmentation">Customer Segmentation</Link></li>
            <li><Link to="/risk">Loan Risk</Link></li>
            <li><Link to="/fees">Fee Optimization</Link></li>
            <li><Link to="/forex">Forex Simulator</Link></li>
          </ul>
        </nav>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/segmentation" element={<SegmentationPage />} />
          <Route path="/risk" element={<LoanRiskPage />} />
          <Route path="/fees" element={<FeeOptimizationPage />} />
          <Route path="/forex" element={<ForexSimulatorPage />} />
        </Routes>
      </div>
    </Router>
  );
}

function Dashboard() {
  return (
    <div className="dashboard">
      <h2>Welcome to NCBA Revenue Maximizer</h2>
      <p>Select a module:</p>
      <ul>
        <li><Link to="/segmentation">Customer Segmentation</Link></li>
        <li><Link to="/risk">Loan Risk Analysis</Link></li>
        <li><Link to="/fees">Fee Optimization</Link></li>
        <li><Link to="/forex">Forex Simulator</Link></li>
      </ul>
    </div>
  );
}

export default App;