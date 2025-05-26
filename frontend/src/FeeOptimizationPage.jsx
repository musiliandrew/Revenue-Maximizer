import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './FeeOptimizationPage.css';

const FeeOptimizationPage = () => {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    axios.get('/api/fee-optimization/')
      .then(response => setData(response.data))
      .catch(err => setError(err.message));
  }, []);

  if (error) return <div>Error: {error}</div>;
  if (!data) return <div>Loading...</div>;

  return (
    <div className="fee-optimization-page" style={{ backgroundColor: '#003087', color: '#FFD700' }}>
      <h1>Fee Optimization Dashboard</h1>
      <h2>Portfolio Overview</h2>
      <p>Total Customers: {data.portfolio.total_customers}</p>
      <p>Total Revenue: ${data.portfolio.total_revenue.toFixed(2)}</p>
      <p>Avg Recommended Fee: ${data.portfolio.avg_recommended_fee.toFixed(2)}</p>
      <p>Avg Churn Risk: {(data.portfolio.avg_churn_risk * 100).toFixed(1)}%</p>

      <h2>Cluster Insights</h2>
      {data.clusters.map(cluster => (
        <div key={cluster.cluster}>
          <h3>Cluster {cluster.cluster}</h3>
          <p>Customer Count: {cluster.customer_count}</p>
          <p>Avg Recommended Fee: ${cluster.avg_recommended_fee.toFixed(2)}</p>
          <p>Total Revenue: ${cluster.total_revenue.toFixed(2)}</p>
          <p>Avg Churn Risk: {(cluster.avg_churn_risk * 100).toFixed(1)}%</p>
          <p>Avg Default Probability: {(cluster.avg_default_probability * 100).toFixed(1)}%</p>
        </div>
      ))}

      <h2>Top Fee Customers</h2>
      <table>
        <thead>
          <tr>
            <th>Customer ID</th>
            <th>Cluster</th>
            <th>Recommended Fee</th>
            <th>Expected Revenue</th>
            <th>Churn Risk</th>
            <th>Default Probability</th>
          </tr>
        </thead>
        <tbody>
          {data.customers
            .sort((a, b) => b.recommended_fee - a.recommended_fee)
            .slice(0, 5)
            .map(customer => (
              <tr key={customer.customer_id}>
                <td>{customer.customer_id}</td>
                <td>{customer.cluster}</td>
                <td>${customer.recommended_fee.toFixed(2)}</td>
                <td>${customer.expected_revenue.toFixed(2)}</td>
                <td>{(customer.churn_risk * 100).toFixed(1)}%</td>
                <td>{(customer.avg_default_probability * 100).toFixed(1)}%</td>
              </tr>
            ))}
        </tbody>
      </table>
    </div>
  );
};

export default FeeOptimizationPage;