import { useState, useEffect } from 'react';
import axios from 'axios';
import { Bar, Line, Scatter } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, LineElement, PointElement, ScatterController, Title, Tooltip, Legend } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, LineElement, PointElement, ScatterController, Title, Tooltip, Legend);

function SegmentationPage() {
  const [clusters, setClusters] = useState([]);
  const [summary, setSummary] = useState({});
  const [elbow, setElbow] = useState({});
  const [error, setError] = useState(null);
  const [showDiaspora, setShowDiaspora] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await axios.get('/api/segmentation/');
        setClusters(showDiaspora
          ? response.data.clusters.filter(c => {
              const customer = response.data.customers.find(cust => cust.customer_id === c.customer_id);
              return customer?.is_diaspora;
            })
          : response.data.clusters
        );
        setSummary(response.data.summary || {});
        setElbow(response.data.elbow || {});
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch segmentation data');
        console.error(err);
        setLoading(false);
      }
    };
    fetchData();
  }, [showDiaspora]);

  const chartData = {
    labels: Object.keys(summary),
    datasets: [
      { label: 'Avg Income', data: Object.values(summary).map(s => s.avg_income || 0), backgroundColor: 'rgba(75, 192, 192, 0.5)' },
      { label: 'Avg Credit Score', data: Object.values(summary).map(s => s.avg_credit_score || 0), backgroundColor: 'rgba(255, 99, 132, 0.5)' },
      { label: 'Avg Savings', data: Object.values(summary).map(s => s.avg_savings_balance || 0), backgroundColor: 'rgba(54, 162, 235, 0.5)' },
      { label: 'Avg Card Value', data: Object.values(summary).map(s => s.avg_card_value || 0), backgroundColor: 'rgba(255, 206, 86, 0.5)' },
      { label: 'Avg Loan Amount', data: Object.values(summary).map(s => s.avg_loan_amount || 0), backgroundColor: 'rgba(153, 102, 255, 0.5)' },
      { label: 'Avg FX Volume', data: Object.values(summary).map(s => s.avg_fx_volume || 0), backgroundColor: 'rgba(255, 159, 64, 0.5)' },
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

  const elbowData = {
    labels: elbow.k || [],
    datasets: [
      {
        label: 'Inertia',
        data: elbow.inertia || [],
        borderColor: '#003087',
        backgroundColor: '#FFD700',
        fill: false,
      },
    ],
  };

  const elbowOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: 'Elbow Method for Optimal Clusters' },
    },
    scales: {
      x: { title: { display: true, text: 'Number of Clusters (k)' } },
      y: { title: { display: true, text: 'Inertia' } },
    },
  };

  const scatterData = {
    datasets: Object.keys(summary).map((cluster, i) => ({
      label: cluster,
      data: clusters
        .filter(c => c.cluster === parseInt(cluster.split(' ')[1]))
        .map(c => {
          const customer = clusters.find(cust => cust.customer_id === c.customer_id);
          return { x: customer?.income || 0, y: customer?.credit_score || 0 };
        }),
      backgroundColor: `rgba(${i * 100}, 99, 132, 0.5)`,
    })),
  };

  const scatterOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: 'Income vs Credit Score' },
    },
    scales: {
      x: { title: { display: true, text: 'Income' } },
      y: { title: { display: true, text: 'Credit Score' } },
    },
  };

  const calculateRevenue = (cluster, summary) => {
    if (!summary[cluster] || !summary[cluster].count) return 'N/A';
    const baseRevenue = summary[cluster].count * 5000;
    const uplift = cluster === 'Cluster 0' ? 2 : cluster === 'Cluster 1' ? 1.5 : 1.2;
    return (baseRevenue * uplift).toLocaleString();
  };

  const insights = {
    'Cluster 0': {
      profile: 'High-income, high-credit-score customers with active loans and cards.',
      actions: [
        'Offer premium credit cards (e.g., Visa Infinite).',
        'Upsell wealth management or investment products.',
        'Target for high-value personal loans.'
      ],
      revenue: 'High revenue potential ($50K-$100K per customer annually).'
    },
    'Cluster 1': {
      profile: 'Middle-income savers with high savings and moderate FX activity.',
      actions: [
        'Promote cashback/rewards credit cards.',
        'Offer fixed-deposit accounts with competitive rates.',
        'Introduce micro-investment options.'
      ],
      revenue: 'Moderate revenue uplift ($10K-$30K per customer).'
    },
    'Cluster 2': {
      profile: 'Low-income customers with poor credit and high churn risk.',
      actions: [
        'Provide financial literacy programs.',
        'Offer secured credit cards or microloans.',
        'Promote mobile banking and low-fee accounts.'
      ],
      revenue: 'Long-term growth ($5K-$15K per customer).'
    }
  };

  if (loading) return <div className="segmentation-page"><p>Loading...</p></div>;
  if (error) return <div className="segmentation-page"><p className="error">{error}</p></div>;

  return (
    <div className="segmentation-page">
      <h1>NCBA Customer Segmentation</h1>
      <button onClick={() => setShowDiaspora(!showDiaspora)}>
        {showDiaspora ? 'Show All Customers' : 'Show Diaspora Only'}
      </button>
      <div className="chart-container">
        <Bar data={chartData} options={chartOptions} />
      </div>
      {elbow.k && (
        <div className="chart-container">
          <Line data={elbowData} options={elbowOptions} />
        </div>
      )}
      <div className="chart-container">
        <Scatter data={scatterData} options={scatterOptions} />
      </div>
      <h2>Cluster Summaries</h2>
      <table>
        <thead>
          <tr>
            <th>Cluster</th>
            <th>Avg Income</th>
            <th>Avg Credit Score</th>
            <th>Avg Savings</th>
            <th>Avg Card Value</th>
            <th>Avg Loan Amount</th>
            <th>Avg FX Volume</th>
            <th>Churn Risk</th>
            <th>Recommended Fee</th>
            <th>Customer Count</th>
            <th>Diaspora Count</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(summary).map(([cluster, stats]) => (
            <tr key={cluster}>
              <td>{cluster}</td>
              <td>${(stats.avg_income || 0).toFixed(2)}</td>
              <td>{(stats.avg_credit_score || 0).toFixed(2)}</td>
              <td>${(stats.avg_savings_balance || 0).toFixed(2)}</td>
              <td>${(stats.avg_card_value || 0).toFixed(2)}</td>
              <td>${(stats.avg_loan_amount || 0).toFixed(2)}</td>
              <td>${(stats.avg_fx_volume || 0).toFixed(2)}</td>
              <td>{((stats.churn_risk || 0) * 100).toFixed(1)}%</td>
              <td>${(stats.recommended_fee || 0).toFixed(2)}</td>
              <td>{stats.count || 0}</td>
              <td>{stats.diaspora_count || 0}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <h2>Insights for NCBA</h2>
      <div className="insights">
        {Object.keys(summary).map(cluster => (
          <div key={cluster} className="cluster-insight">
            <h3>{cluster}</h3>
            <p><strong>Profile:</strong> {insights[cluster]?.profile || 'N/A'}</p>
            <p><strong>Churn Risk:</strong> {((summary[cluster]?.churn_risk || 0) * 100).toFixed(1)}%</p>
            <p><strong>Recommended Fee:</strong> ${summary[cluster]?.recommended_fee?.toFixed(2) || 'N/A'}</p>
            <p><strong>Actions:</strong></p>
            <ul>{insights[cluster]?.actions?.map((action, i) => <li key={i}>{action}</li>) || <li>No actions available</li>}</ul>
            <p><strong>Revenue Potential:</strong> {insights[cluster]?.revenue || 'N/A'}</p>
            <p><strong>Estimated Revenue:</strong> ${calculateRevenue(cluster, summary)}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default SegmentationPage;