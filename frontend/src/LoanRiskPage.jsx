import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
import './LoanRiskPage.css';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const LoanRiskPage = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/loan-risk/');
        setData(response.data);
        setLoading(false);
      } catch {
        setError('Failed to load loan risk data');
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>{error}</div>;
  if (!data) return <div>No data available</div>;

  // Bar chart: Risk category distribution
  const barData = {
    labels: ['High', 'Medium', 'Low'],
    datasets: [{
      label: 'Number of Loans',
      data: [
        data.portfolio.high_risk_loans,
        data.portfolio.medium_risk_loans,
        data.portfolio.low_risk_loans
      ],
      backgroundColor: ['#FF5733', '#FFD700', '#003087'],
      borderColor: '#000',
      borderWidth: 1
    }]
  };

  return (
    <div className="loan-risk-container">
      <h1 style={{ color: '#003087' }}>NCBA Loan Default Risk Predictor</h1>
      
      <div className="portfolio-summary">
        <h2>Portfolio Overview</h2>
        <p>Total Loans: {data.portfolio.total_loans}</p>
        <p>High Risk (&gt;50%): {data.portfolio.high_risk_loans} ({((data.portfolio.high_risk_loans / data.portfolio.total_loans) * 100).toFixed(1)}%)</p>
        <p>Medium Risk (20-50%): {data.portfolio.medium_risk_loans}</p>
        <p>Low Risk (&lt;20%): {data.portfolio.low_risk_loans}</p>
        <p>Average Default Probability: {(data.portfolio.avg_default_probability * 100).toFixed(1)}%</p>
      </div>

      <div className="chart-container">
        <h2>Risk Category Distribution</h2>
        <Bar
          data={barData}
          options={{
            scales: {
              y: { title: { display: true, text: 'Number of Loans' } }
            },
            plugins: { legend: { display: true } }
          }}
        />
      </div>

      <div className="table-container">
        <h2>Loan Risk Details</h2>
        <table>
          <thead>
            <tr>
              <th>Loan ID</th>
              <th>Customer ID</th>
              <th>Default Probability</th>
              <th>Risk Category</th>
            </tr>
          </thead>
          <tbody>
            {data.loans.map(loan => (
              <tr key={loan.loan_id}>
                <td>{loan.loan_id}</td>
                <td>{loan.customer_id}</td>
                <td>{(loan.default_probability * 100).toFixed(1)}%</td>
                <td>{loan.risk_category}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default LoanRiskPage;