import { useEffect, useState } from 'react';
import axios from 'axios';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
import './App.css';

// Register Chart.js components
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

function App() {
  const [clusters, setClusters] = useState([]);
  const [summary, setSummary] = useState({});
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(`${import.meta.env.VITE_API_URL}/api/segmentation/`);
        setClusters(response.data.clusters);
        setSummary(response.data.summary);
      } catch (err) {
        setError('Failed to fetch segmentation data');
        console.error(err);
      }
    };
    fetchData();
  }, []);

  // Prepare chart data
  const chartData = {
    labels: Object.keys(summary),
    datasets: [
      {
        label: 'Average Income',
        data: Object.values(summary).map(s => s.avg_income),
        backgroundColor: 'rgba(75, 192, 192, 0.5)',
      },
      {
        label: 'Average Credit Score',
        data: Object.values(summary).map(s => s.avg_credit_score),
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
      },
      {
        label: 'Average Savings Balance',
        data: Object.values(summary).map(s => s.avg_savings_balance),
        backgroundColor: 'rgba(54, 162, 235, 0.5)',
      },
      {
        label: 'Average Card Value',
        data: Object.values(summary).map(s => s.avg_card_value),
        backgroundColor: 'rgba(255, 206, 86, 0.5)',
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: 'Customer Segment Averages' },
    },
    scales: {
      y: { beginAtZero: true, title: { display: true, text: 'Value' } },
      x: { title: { display: true, text: 'Cluster' } },
    },
  };

  return (
    <div className="App">
      <h1>NCBA Customer Segmentation</h1>
      {error && <p className="error">{error}</p>}
      <div className="chart-container">
        <Bar data={chartData} options={chartOptions} />
      </div>
      <h2>Cluster Summaries</h2>
      <table>
        <thead>
          <tr>
            <th>Cluster</th>
            <th>Avg Income</th>
            <th>Avg Credit Score</th>
            <th>Avg Savings Balance</th>
            <th>Avg Card Value</th>
            <th>Customer Count</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(summary).map(([cluster, stats]) => (
            <tr key={cluster}>
              <td>{cluster}</td>
              <td>${stats.avg_income.toFixed(2)}</td>
              <td>{stats.avg_credit_score.toFixed(2)}</td>
              <td>${stats.avg_savings_balance.toFixed(2)}</td>
              <td>${stats.avg_card_value.toFixed(2)}</td>
              <td>{clusters.filter(c => c.cluster === parseInt(cluster.split(' ')[1])).length}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;