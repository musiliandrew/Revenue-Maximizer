import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Bar, Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import './ForexSimulatorPage.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend
);

const ForexSimulatorPage = () => {
  const [data, setData] = useState({
    corridors: [],
    forecast: [],
    recommendations: []
  });

  useEffect(() => {
    // Replace with your actual API endpoint
    axios.get('/api/forex-simulator-data')
      .then(res => setData(res.data))
      .catch(err => console.error(err));
  }, []);

  return (
    <div className="forex-simulator-page">
      <h2>Margin by Corridor</h2>
      {/* Bar Chart for Margin by Corridor */}
      <Bar
        data={{
          labels: data.corridors.map(c => c.currency_pair),
          datasets: [{
            label: "Total Margin ($)",
            data: data.corridors.map(c => c.total_margin_usd),
            backgroundColor: ["#FFD700", "#FFFFFF", "#FF6347"],
            borderColor: ["#003087", "#003087", "#003087"],
            borderWidth: 1
          }]
        }}
        options={{
          scales: {
            y: {
              beginAtZero: true,
              title: { display: true, text: "Margin ($)", color: "#FFFFFF" },
              ticks: { color: "#FFFFFF" }
            },
            x: {
              title: { display: true, text: "Currency Pair", color: "#FFFFFF" },
              ticks: { color: "#FFFFFF" }
            }
          },
          plugins: {
            legend: { labels: { color: "#FFFFFF" } }
          }
        }}
      />

      <h2>USD/KES Forecast (30 Days)</h2>
      {/* Line Chart for USD/KES Forecast */}
      <Line
        data={{
          labels: data.forecast.map(f => f.date),
          datasets: [{
            label: "Forecasted Ask Rate",
            data: data.forecast.map(f => f.forecasted_ask_rate),
            borderColor: "#FFD700",
            backgroundColor: "rgba(255, 215, 0, 0.2)",
            fill: true,
            tension: 0.3
          }]
        }}
        options={{
          scales: {
            y: {
              title: { display: true, text: "Ask Rate", color: "#FFFFFF" },
              ticks: { color: "#FFFFFF" }
            },
            x: {
              title: { display: true, text: "Date", color: "#FFFFFF" },
              ticks: { color: "#FFFFFF" }
            }
          },
          plugins: {
            legend: { labels: { color: "#FFFFFF" } }
          }
        }}
      />

      <h2>Recommendations</h2>
      <ul>
        {data.recommendations.map((rec, idx) => (
          <li key={idx}>
            <strong>{rec.action}</strong>: {rec.reason} (Impact: {rec.impact})
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ForexSimulatorPage;