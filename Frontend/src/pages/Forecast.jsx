import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Tooltip,
  Legend,
} from 'chart.js';
import './Forecast.css';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import React, { useEffect, useState } from 'react';

ChartJS.register(LineElement, CategoryScale, LinearScale, PointElement, Tooltip, Legend);

function Forecast() {
  const [forecastData, setForecastData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    axios.get(`https://aqi-forecasting-webapp-1.onrender.com/api/get_forecast`)
      .then((response) => {
        setForecastData(response.data);  // Axios automatically parses JSON for you
        setLoading(false);
      })
      .catch((err) => {
        console.error('Axios error:', err);
        setError(true);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="loading">Loading forecast...</div>;
  if (error || !forecastData) return <div className="error">Could not load forecast data.</div>;

  // Extract labels and values from the forecastData array
  const labels = forecastData.map((item) => item.predicted_date); // Date for x-axis
  const values = forecastData.map((item) => item.predicted_aqi); // AQI values for y-axis

  // Chart data setup
  const chartData = {
    labels: labels,
    datasets: [
      {
        label: 'Forecasted AQI',
        data: values,
        fill: true,
        borderColor: '#facc15',
        backgroundColor: 'rgba(250, 204, 21, 0.2)',
        tension: 0.4,
        pointBackgroundColor: '#facc15',
        pointRadius: 4,
      },
    ],
  };

  // Chart options
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        labels: {
          color: '#facc15',
        },
      },
      tooltip: {
        enabled: true,
      },
    },
    scales: {
      x: {
        ticks: {
          color: '#fff',
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
        },
      },
      y: {
        ticks: {
          color: '#fff',
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
        },
      },
    },
  };

  // Custom plugin to display values on top of points
  const valueLabelsPlugin = {
    id: 'valueLabels',
    afterDatasetsDraw(chart) {
      const { ctx } = chart;
      chart.data.datasets.forEach((dataset, datasetIndex) => {
        const meta = chart.getDatasetMeta(datasetIndex);
        meta.data.forEach((point, index) => {
          const value = dataset.data[index].toFixed(0); // Format the value to 2 decimal places
          ctx.save();
          ctx.font = '14px Arial';
          ctx.fillStyle = '#facc15'; // Yellow text color
          ctx.textAlign = 'center';
          ctx.fillText(value, point.x, point.y - 15); // Position the text above the point
          ctx.restore();
        });
      });
    },
  };

  return (
    <div className="forecast-container">
      <h2 className="forecast-title">7-Day AQI Forecast</h2> {/* Title moved outside the chart container */}
      <div className="chart-container">
        <Line data={chartData} options={options} plugins={[valueLabelsPlugin]} />
      </div>
    </div>
  );
}

export default Forecast;